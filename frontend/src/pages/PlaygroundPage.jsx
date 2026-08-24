import React, { useEffect, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Room, RoomEvent, Track } from 'livekit-client';
import { agentsApi, playgroundApi } from '../api.js';
import TranscriptView from '../components/TranscriptView.jsx';
import LatencyPanel from '../components/LatencyPanel.jsx';

const PHASES = {
  SETUP: 'setup',
  CONNECTING: 'connecting',
  IN_CALL: 'in_call',
  ENDED: 'ended',
  TEXT: 'text',
};

const MODES = {
  VOICE: 'voice',
  TEXT: 'text',
};

const MIC_SPEAK_THRESHOLD = 0.12;
const BARGE_DECAY_MS = 650;

function fmtClock(ms) {
  const s = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
}

function confidenceClass(v) {
  const n = typeof v === 'number' ? v : Number(v);
  if (v == null || Number.isNaN(n)) return '';
  const pct = n <= 1 ? n * 100 : n;
  return pct >= 80 ? 'chip-green' : pct >= 50 ? 'badge-amber' : 'chip-red';
}

export default function PlaygroundPage() {
  const params = useParams();
  const routeVersionId = params.agentVersionId ? Number(params.agentVersionId) : null;

  const [phase, setPhase] = useState(PHASES.SETUP);
  const [mode, setMode] = useState(MODES.VOICE); // voice (mic) | text

  // ---- setup ----
  const [agents, setAgents] = useState(null);
  const [agentsError, setAgentsError] = useState(null);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [versions, setVersions] = useState([]);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [selectedVersionId, setSelectedVersionId] = useState(routeVersionId || '');
  const [versionInfo, setVersionInfo] = useState(null); // {agentName, version}
  const [infoError, setInfoError] = useState(null);

  // ---- live session (voice mode) ----
  const [connectError, setConnectError] = useState(null);
  const [statusNote, setStatusNote] = useState(null);
  const [fatalError, setFatalError] = useState(null);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [micLevel, setMicLevel] = useState(0);
  const [bargeIn, setBargeIn] = useState(false);
  const [captions, setCaptions] = useState([]);

  // ---- text session ----
  const [chatMessages, setChatMessages] = useState([]); // [{speaker:'caller'|'agent', text}]
  const [chatInput, setChatInput] = useState('');
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState(null);
  const [chatDone, setChatDone] = useState(false);
  const [liveFields, setLiveFields] = useState([]); // extracted so far

  // ---- post-call ----
  const [result, setResult] = useState(null);
  const [completeError, setCompleteError] = useState(null);
  const [completing, setCompleting] = useState(false);

  // refs (mutable values not rendered directly)
  const roomRef = useRef(null);
  const sessionRef = useRef(null);
  const micTrackRef = useRef(null);
  const timerRef = useRef(null);
  const levelTimerRef = useRef(null);
  const startedAtRef = useRef(0);
  const userEndedRef = useRef(false);
  const reconnectTriesRef = useRef(0);
  const remotePlayingRef = useRef(false);
  const bargeUntilRef = useRef(0);
  const audioElsRef = useRef([]);

  // ---- load agents for the picker (only when no version in the URL) ----
  useEffect(() => {
    if (routeVersionId) return;
    let cancelled = false;
    setAgentsError(null);
    agentsApi
      .list()
      .then((list) => {
        if (cancelled) return;
        const rows = Array.isArray(list) ? list : [];
        setAgents(rows);
        if (rows.length > 0) setSelectedAgentId((prev) => prev || String(rows[0].id));
      })
      .catch((e) => !cancelled && setAgentsError(e.message || String(e)));
    return () => {
      cancelled = true;
    };
  }, [routeVersionId]);

  // ---- load version list when the picked agent changes ----
  useEffect(() => {
    if (routeVersionId || !selectedAgentId) return;
    let cancelled = false;
    setVersionsLoading(true);
    agentsApi
      .listVersions(selectedAgentId)
      .then((list) => {
        if (cancelled) return;
        const rows = Array.isArray(list) ? list.slice().reverse() : [];
        setVersions(rows);
        setSelectedVersionId((prev) => {
          if (prev && rows.some((v) => String(v.id) === String(prev))) return prev;
          return rows.length ? String(rows[0].id) : '';
        });
      })
      .catch(() => {
        if (!cancelled) setVersions([]);
      })
      .finally(() => !cancelled && setVersionsLoading(false));
    return () => {
      cancelled = true;
    };
  }, [routeVersionId, selectedAgentId]);

  // ---- resolve header info for whichever version is active ----
  useEffect(() => {
    if (!selectedVersionId) {
      setVersionInfo(null);
      return;
    }
    let cancelled = false;
    setInfoError(null);
    agentsApi
      .getVersion(selectedVersionId)
      .then(async (v) => {
        if (cancelled) return;
        let agentName = '';
        try {
          const a = await agentsApi.get(v.agent_id);
          agentName = a.name;
        } catch {
          /* header still renders without the agent name */
        }
        setVersionInfo({ agentName, version: v.version });
      })
      .catch((e) => !cancelled && setInfoError(e.message || String(e)));
    return () => {
      cancelled = true;
    };
  }, [selectedVersionId]);

  // ---- teardown on unmount ----
  useEffect(
    () => () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (levelTimerRef.current) clearInterval(levelTimerRef.current);
      try {
        roomRef.current && roomRef.current.disconnect();
      } catch {
        /* already gone */
      }
    },
    []
  );

  function startTimers() {
    if (timerRef.current) clearInterval(timerRef.current);
    if (levelTimerRef.current) clearInterval(levelTimerRef.current);
    startedAtRef.current = Date.now();
    setElapsedMs(0);
    timerRef.current = setInterval(() => setElapsedMs(Date.now() - startedAtRef.current), 500);
    levelTimerRef.current = setInterval(pollMicLevel, 150);
  }

  function stopTimers() {
    if (timerRef.current) clearInterval(timerRef.current);
    if (levelTimerRef.current) clearInterval(levelTimerRef.current);
    timerRef.current = null;
    levelTimerRef.current = null;
  }

  function pollMicLevel() {
    const track = micTrackRef.current;
    let vol = 0;
    if (track && typeof track.getVolume === 'function') {
      try {
        vol = track.getVolume() || 0;
      } catch {
        vol = 0;
      }
    }
    setMicLevel(vol);
    const now = Date.now();
    if (vol > MIC_SPEAK_THRESHOLD && remotePlayingRef.current) {
      bargeUntilRef.current = now + BARGE_DECAY_MS;
      setBargeIn(true);
    } else if (now > bargeUntilRef.current) {
      setBargeIn(false);
    }
  }

  function attachRemoteAudio(track) {
    const el = document.createElement('audio');
    el.autoplay = true;
    el.style.display = 'none';
    document.body.appendChild(el);
    try {
      track.attach(el);
    } catch {
      el.remove();
      return;
    }
    audioElsRef.current.push({ track, el });
  }

  function detachAllAudio() {
    audioElsRef.current.forEach(({ track, el }) => {
      try {
        track.detach(el);
      } catch {
        /* noop */
      }
      try {
        el.remove();
      } catch {
        /* noop */
      }
    });
    audioElsRef.current = [];
    remotePlayingRef.current = false;
  }

  function handleCaption(payload, participant) {
    let text = '';
    let speaker = '';
    try {
      const decoded = new TextDecoder().decode(payload);
      try {
        const obj = JSON.parse(decoded);
        text = typeof obj === 'string' ? obj : String((obj && obj.text) || '');
        speaker = (obj && obj.speaker) || '';
      } catch {
        text = decoded;
      }
    } catch {
      return;
    }
    if (!text.trim()) return;
    setCaptions((prev) =>
      [
        ...prev,
        { speaker: speaker || (participant && participant.identity) || 'agent', text, ts: Date.now() },
      ].slice(-200)
    );
  }

  async function joinWithSession(sess) {
    const room = new Room({ adaptiveStream: true, dynacast: true });

    room.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind === Track.Kind.Audio) {
        attachRemoteAudio(track);
        remotePlayingRef.current = true;
      }
    });
    room.on(RoomEvent.TrackUnsubscribed, (track) => {
      if (track.kind === Track.Kind.Audio) {
        audioElsRef.current = audioElsRef.current.filter((a) => a.track !== track);
        if (audioElsRef.current.length === 0) remotePlayingRef.current = false;
      }
    });
    room.on(RoomEvent.DataReceived, handleCaption);
    room.on(RoomEvent.Reconnecting, () => setStatusNote('Connection hiccup — recovering…'));
    room.on(RoomEvent.Reconnected, () => setStatusNote(null));

    // Hard disconnect: either the user hung up or the room dropped. One
    // automatic rejoin is attempted; after that an error card takes over.
    room.on(RoomEvent.Disconnected, () => {
      stopTimers();
      if (userEndedRef.current) return;
      if (reconnectTriesRef.current < 1 && sessionRef.current) {
        reconnectTriesRef.current += 1;
        setStatusNote('Connection lost — automatically rejoining…');
        setTimeout(async () => {
          try {
            await joinWithSession(sessionRef.current);
            setStatusNote(null);
            startTimers();
          } catch (e) {
            setStatusNote(null);
            setFatalError(
              `Lost the connection to the voice room and could not rejoin (${e.message || e}). Nothing you said is lost — press "Back to setup" and start again.`
            );
          }
        }, 900);
      } else {
        setFatalError('The connection to the voice room dropped.');
      }
    });

    await room.connect(sess.livekit_url, sess.livekit_token);
    await room.localParticipant.setMicrophoneEnabled(true);

    const pub = room.localParticipant.getTrackPublication(Track.Source.Microphone);
    micTrackRef.current = pub && pub.audioTrack ? pub.audioTrack : null;

    roomRef.current = room;
  }

  async function startCall() {
    if (!selectedVersionId) return;
    setPhase(PHASES.CONNECTING);
    setConnectError(null);
    setFatalError(null);
    setResult(null);
    setCompleteError(null);
    setCaptions([]);
    userEndedRef.current = false;
    reconnectTriesRef.current = 0;
    remotePlayingRef.current = false;
    setBargeIn(false);

    // Trigger the browser mic prompt explicitly so a denial surfaces as a
    // clear message instead of a cryptic room error.
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop());
    } catch {
      setConnectError(
        'Microphone access was blocked. Allow microphone permission for this site (check the address-bar icon), then press Start again.'
      );
      setPhase(PHASES.SETUP);
      return;
    }

    let sess;
    try {
      sess = await playgroundApi.startSession(Number(selectedVersionId));
      sessionRef.current = sess;
    } catch (e) {
      setConnectError(e.message || 'Could not start a playground session.');
      setPhase(PHASES.SETUP);
      return;
    }

    try {
      await joinWithSession(sess);
      startTimers();
      setPhase(PHASES.IN_CALL);
    } catch (e) {
      setConnectError(e.message || 'Could not join the voice room.');
      try {
        roomRef.current && roomRef.current.disconnect();
      } catch {
        /* noop */
      }
      roomRef.current = null;
      setPhase(PHASES.SETUP);
    }
  }

  async function endCall() {
    userEndedRef.current = true;
    stopTimers();
    try {
      roomRef.current && roomRef.current.disconnect();
    } catch {
      /* noop */
    }
    roomRef.current = null;
    micTrackRef.current = null;
    setPhase(PHASES.ENDED);
    await completeSession();
  }

  async function completeSession() {
    if (!sessionRef.current) return;
    setCompleting(true);
    setCompleteError(null);
    try {
      const res = await playgroundApi.completeSession(sessionRef.current.call_id);
      setResult(res || {});
    } catch (e) {
      setCompleteError(e.message || 'Could not finalize the session.');
    } finally {
      setCompleting(false);
    }
  }

  function backToSetup() {
    stopTimers();
    detachAllAudio();
    sessionRef.current = null;
    micTrackRef.current = null;
    setResult(null);
    setFatalError(null);
    setConnectError(null);
    setStatusNote(null);
    setCaptions([]);
    setElapsedMs(0);
    setBargeIn(false);
    // text mode
    setChatMessages([]);
    setChatInput('');
    setChatBusy(false);
    setChatError(null);
    setChatDone(false);
    setLiveFields([]);
    setPhase(PHASES.SETUP);
  }

  // ------------------------------------------------------- text mode handlers

  function applyTurnResponse(res) {
    if (!res) return;
    if (res.reply_text) {
      setChatMessages((prev) => [...prev, { speaker: 'agent', text: res.reply_text }]);
    }
    if (Array.isArray(res.extracted_fields) && res.extracted_fields.length > 0) {
      setLiveFields((prev) => {
        const byName = new Map(prev.map((f) => [f.field_name, f]));
        res.extracted_fields.forEach((f) => byName.set(f.field_name, f));
        return Array.from(byName.values());
      });
    }
    if (res.done) setChatDone(true);
  }

  async function startTextCall() {
    if (!selectedVersionId || chatBusy) return;
    setResult(null);
    setFatalError(null);
    setConnectError(null);
    setChatMessages([]);
    setLiveFields([]);
    setChatDone(false);
    setChatError(null);
    userEndedRef.current = false;

    let sess = null;
    try {
      sess = await playgroundApi.startSession(Number(selectedVersionId));
      sessionRef.current = sess; // same record shape as voice mode
    } catch (e) {
      setConnectError(e.message || 'Could not start a playground session.');
      return;
    }

    setPhase(PHASES.TEXT); // no LiveKit join — straight to the chat panel
    setChatBusy(true);
    try {
      const res = await playgroundApi.sendTurn(sess.call_id, { event: 'start' });
      applyTurnResponse(res);
    } catch (e) {
      setChatError(e.message || 'The agent could not start the conversation.');
    } finally {
      setChatBusy(false);
    }
  }

  async function sendText(e) {
    e.preventDefault();
    const text = chatInput.trim();
    if (!text || chatBusy || chatDone || !sessionRef.current) return;
    setChatMessages((prev) => [...prev, { speaker: 'caller', text }]);
    setChatInput('');
    setChatBusy(true);
    setChatError(null);
    try {
      const res = await playgroundApi.sendTurn(sessionRef.current.call_id, { text });
      applyTurnResponse(res);
    } catch (err) {
      setChatError(err.message || 'Could not send that message.');
    } finally {
      setChatBusy(false);
    }
  }

  async function finishTextSession() {
    if (!sessionRef.current) return;
    setCompleting(true);
    setCompleteError(null);
    try {
      const res = await playgroundApi.completeSession(sessionRef.current.call_id);
      setResult(res || {});
      setPhase(PHASES.ENDED); // reuse the full voice-mode report view
    } catch (e) {
      setCompleteError(e.message || 'Could not finalize the session.');
    } finally {
      setCompleting(false);
    }
  }

  // ------------------------------------------------------------------ render

  const chatLogRef = useRef(null);
  useEffect(() => {
    const el = chatLogRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [chatMessages, chatBusy]);

  function renderFieldsTable(fields) {
    return (
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Field</th>
              <th>Value</th>
              <th style={{ width: '130px' }}>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {fields.map((f, i) => (
              <tr key={`${f.field_name}-${i}`}>
                <td className="cell-strong">{f.field_name}</td>
                <td>{f.field_value != null ? String(f.field_value) : '—'}</td>
                <td>
                  <span className={`badge ${confidenceClass(f.confidence) || 'badge-gray'}`}>
                    {f.confidence != null && !Number.isNaN(Number(f.confidence))
                      ? `${Math.round(
                          Number(f.confidence) <= 1 ? Number(f.confidence) * 100 : Number(f.confidence)
                        )}%`
                      : '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (phase === PHASES.TEXT) {
    return (
      <div className="narrow-wide">
        <div className="page-head">
          <div>
            <h2 className="page-title">Playground — text mode</h2>
            <p className="page-sub">
              Same agent, same conversation flow — typed instead of spoken. Everything is recorded exactly like a
              voice test.
            </p>
          </div>
        </div>

        <div className="card chat-panel">
          <div className="form-actions space-between">
            <span className="meta-line">
              {versionInfo && (
                <>
                  <span>
                    <strong>Agent:</strong> {versionInfo.agentName || '(unknown)'}
                  </span>
                  <span>
                    <strong>Version:</strong> v{versionInfo.version}
                  </span>
                </>
              )}
            </span>
            <div>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => {
                  userEndedRef.current = true;
                  finishTextSession();
                }}
                disabled={completing}
              >
                {completing ? 'Finishing…' : 'End session & show report'}
              </button>
              <button type="button" className="btn btn-secondary btn-sm" onClick={backToSetup}>
                Back to setup
              </button>
            </div>
          </div>

          <div className="chat-log" ref={chatLogRef}>
            {chatMessages.length === 0 && !chatBusy && (
              <p className="hint">Starting the conversation…</p>
            )}
            {chatMessages.map((m, i) => (
              <div key={i} className={`chat-row ${m.speaker === 'caller' ? 'caller' : 'agent'}`}>
                <div className={`chat-bubble ${m.speaker === 'caller' ? 'bubble-caller' : 'bubble-agent'}`}>
                  {m.text}
                </div>
              </div>
            ))}
            {chatBusy && (
              <div className="chat-row agent">
                <div className="chat-bubble bubble-agent hint">Typing…</div>
              </div>
            )}
          </div>

          {chatError && <div className="banner banner-error">{chatError}</div>}

          {chatDone && (
            <div className="banner banner-success">
              <strong>Conversation complete.</strong> The agent ended this session.
            </div>
          )}

          {liveFields.length > 0 && (
            <div>
              <h3 className="card-title">Extracted so far</h3>
              {renderFieldsTable(liveFields)}
            </div>
          )}

          {!chatDone ? (
            <form className="chat-input-row" onSubmit={sendText}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type your reply…"
                disabled={chatBusy}
                autoFocus
                aria-label="Your message"
              />
              <button type="submit" className="btn btn-primary" disabled={chatBusy || !chatInput.trim()}>
                Send
              </button>
            </form>
          ) : (
            <div className="form-actions">
              <button type="button" className="btn btn-primary" onClick={finishTextSession} disabled={completing}>
                {completing ? 'Collecting results…' : 'View full report'}
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (phase === PHASES.IN_CALL || phase === PHASES.CONNECTING) {
    const connecting = phase === PHASES.CONNECTING;
    const speaking = micLevel > MIC_SPEAK_THRESHOLD;
    return (
      <div className="playground-live">
        <div className="card playground-console">
          <div className="playground-status">
            <div className="playground-timer" aria-label={`Call duration ${fmtClock(elapsedMs)}`}>
              {fmtClock(elapsedMs)}
            </div>
            {connecting ? (
              <span className="live-indicator big">
                <span className="spinner spinner-inline" /> Connecting…
              </span>
            ) : (
              <span className={`live-indicator big${speaking ? ' speaking' : ''}`}>
                <span className="live-dot" /> {speaking ? 'Listening…' : 'Agent on the line'}
              </span>
            )}
            {bargeIn && (
              <span className="badge badge-orange barge-badge" title="You spoke while the agent was talking">
                Barge-in detected
              </span>
            )}
          </div>

          <div className="playground-meter" aria-hidden="true">
            <div className="playground-meter-fill" style={{ width: `${Math.min(100, micLevel * 160)}%` }} />
          </div>

          <p className="hint">
            Talk naturally — you can interrupt the agent mid-sentence and it will stop and listen. Press{' '}
            <strong>End call</strong> when done; the transcript and results appear right after.
          </p>

          <div className="form-actions">
            <button type="button" className="btn btn-danger btn-lg" onClick={endCall} disabled={connecting}>
              End call
            </button>
          </div>
        </div>

        {statusNote && <div className="banner banner-info">{statusNote}</div>}

        <div className="card">
          <h3 className="card-title">Live captions</h3>
          {captions.length === 0 ? (
            <p className="hint">Waiting for captions… (they stream in here as the conversation progresses)</p>
          ) : (
            <TranscriptView turns={captions.slice(-8)} emptyText="No captions." />
          )}
        </div>
      </div>
    );
  }

  if (phase === PHASES.ENDED) {
    const turns = (result && result.transcript) || [];
    const fields = (result && result.extracted_fields) || [];
    return (
      <div className="stack">
        <button type="button" className="btn btn-ghost self-start" onClick={backToSetup}>
          ← Run another test
        </button>

        <div className="banner banner-success">
          <strong>Call finished.</strong>{' '}
          {result && result.duration_seconds != null && <>Duration: {fmtClock(result.duration_seconds * 1000)}. </>}
          {result && result.flagged_for_human ? 'This session was flagged for human review.' : null}
        </div>

        {completeError && (
          <div className="banner banner-error">
            {completeError}{' '}
            <button type="button" className="btn btn-secondary btn-sm" onClick={completeSession} disabled={completing}>
              {completing ? 'Retrying…' : 'Retry'}
            </button>
          </div>
        )}

        {!result && !completeError && (
          <div className="loading-page">
            <span className="spinner" /> Collecting transcript and results…
          </div>
        )}

        {result && (
          <>
            <div className="card">
              <h3 className="card-title">Extracted fields</h3>
              {fields.length === 0 ? (
                <p className="hint">No structured fields were extracted during this call.</p>
              ) : (
                renderFieldsTable(fields)
              )}
              {result.outcome ? (
                <p className="hint">
                  Outcome: <span className="chip">{String(result.outcome)}</span>
                </p>
              ) : null}
            </div>

            <div className="card">
              <h3 className="card-title">Latency</h3>
              <LatencyPanel turns={turns} summary={result.latency} />
            </div>

            <div className="card">
              <h3 className="card-title">Transcript</h3>
              <TranscriptView turns={turns} emptyText="No transcript was recorded for this session." />
            </div>

            {versionInfo && versionInfo.agentName && (
              <p className="hint">
                Tested <strong>{versionInfo.agentName}</strong> v{versionInfo.version}.{' '}
                <Link to="/agents">Back to agents</Link> · <Link to="/campaigns">Launch this agent as a campaign</Link>
              </p>
            )}
          </>
        )}
      </div>
    );
  }

  // ------------------------------------------------------------------ setup

  return (
    <div className="narrow-wide">
      <div className="page-head">
        <div>
          <h2 className="page-title">Playground</h2>
          <p className="page-sub">
            Test any saved agent version straight from this browser — speak over your microphone or type in Text mode.
            Nothing is dialed, so it costs zero telephony minutes.
          </p>
        </div>
      </div>

      {fatalError ? (
        <div className="stack">
          <div className="banner banner-error">{fatalError}</div>
          <div className="card">
            <div className="form-actions">
              <button type="button" className="btn btn-primary" onClick={backToSetup}>
                Back to setup
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="stack">
          <div className="tab-row" role="tablist" aria-label="Test mode">
            <button
              type="button"
              role="tab"
              aria-selected={mode === MODES.VOICE}
              className={`tab-btn${mode === MODES.VOICE ? ' active' : ''}`}
              onClick={() => {
                setMode(MODES.VOICE);
                setConnectError(null);
              }}
            >
              Voice (mic)
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === MODES.TEXT}
              className={`tab-btn${mode === MODES.TEXT ? ' active' : ''}`}
              onClick={() => {
                setMode(MODES.TEXT);
                setConnectError(null);
              }}
            >
              Text
            </button>
          </div>

          {!routeVersionId && (
            <div className="card">
              <h3 className="card-title">Choose what to test</h3>
              {agentsError && (
                <div className="banner banner-error">
                  {agentsError}{' '}
                  <Link to="/agents/new" className="btn btn-secondary btn-sm">
                    Create an agent
                  </Link>
                </div>
              )}
              {!agentsError && agents && agents.length === 0 && (
                <div className="empty-state">
                  No agents yet — build one first.
                  <div className="form-actions">
                    <Link to="/agents/new" className="btn btn-primary">
                      + New Agent
                    </Link>
                  </div>
                </div>
              )}
              {!agentsError && agents && agents.length > 0 && (
                <div className="picker-row">
                  <div className="field">
                    <label htmlFor="pg-agent">Agent</label>
                    <select
                      id="pg-agent"
                      value={selectedAgentId}
                      onChange={(e) => setSelectedAgentId(e.target.value)}
                    >
                      {agents.map((a) => (
                        <option key={a.id} value={a.id}>
                          {a.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="field">
                    <label htmlFor="pg-version">Version</label>
                    <select
                      id="pg-version"
                      value={selectedVersionId}
                      onChange={(e) => setSelectedVersionId(e.target.value)}
                      disabled={versionsLoading}
                    >
                      {versionsLoading && <option>Loading…</option>}
                      {!versionsLoading &&
                        versions.map((v) => (
                          <option key={v.id} value={v.id}>
                            v{v.version} — saved {new Date(v.created_at).toLocaleString()}
                          </option>
                        ))}
                      {!versionsLoading && versions.length === 0 && <option value="">No saved versions yet</option>}
                    </select>
                  </div>
                </div>
              )}
              {infoError && <p className="hint hint-error">{infoError}</p>}
            </div>
          )}

          {selectedVersionId && mode === MODES.VOICE && (
            <>
              <div className="card">
                <h3 className="card-title">Before you start</h3>
                <p>
                  Your browser will ask for microphone permission — this is required so the agent can hear you. Audio
                  plays through your speakers or headset, exactly like a phone call. The whole conversation is recorded
                  as a test session you can review afterwards.
                </p>
                <p className="hint">
                  Tip: use headphones to avoid echo. If nothing seems to happen, check that the correct microphone is
                  selected in your browser's site settings.
                </p>
              </div>
              <div className="card">
                <h3 className="card-title">Ready to talk</h3>
                {versionInfo ? (
                  <p className="meta-line">
                    <span>
                      <strong>Agent:</strong> {versionInfo.agentName || '(unknown)'}
                    </span>
                    <span>
                      <strong>Version:</strong> v{versionInfo.version}
                    </span>
                  </p>
                ) : (
                  <p className="hint">Loading version details…</p>
                )}
                {connectError && <div className="banner banner-error">{connectError}</div>}
                <div className="form-actions">
                  <button
                    type="button"
                    className="btn btn-primary btn-lg"
                    onClick={startCall}
                    disabled={phase === PHASES.CONNECTING || !selectedVersionId}
                  >
                    {phase === PHASES.CONNECTING ? 'Connecting…' : 'Enable microphone & start call'}
                  </button>
                </div>
              </div>
            </>
          )}

          {selectedVersionId && mode === MODES.TEXT && (
            <div className="card">
              <h3 className="card-title">Ready to chat</h3>
              {versionInfo ? (
                <p className="meta-line">
                  <span>
                    <strong>Agent:</strong> {versionInfo.agentName || '(unknown)'}
                  </span>
                  <span>
                    <strong>Version:</strong> v{versionInfo.version}
                  </span>
                </p>
              ) : (
                <p className="hint">Loading version details…</p>
              )}
              <p className="hint">
                No microphone or voice room needed. The agent opens with its disclosure and first question; reply by
                typing. Extraction and the final report work exactly like a voice test.
              </p>
              {connectError && <div className="banner banner-error">{connectError}</div>}
              <div className="form-actions">
                <button type="button" className="btn btn-primary btn-lg" onClick={startTextCall}>
                  Start text test call
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
