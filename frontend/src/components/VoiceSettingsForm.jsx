import React from 'react';

const LANGUAGES = [
  { value: 'en', label: 'English (en)' },
  { value: 'en-IN', label: 'English — India (en-IN)' },
  { value: 'en-US', label: 'English — US (en-US)' },
];

/**
 * Voice settings form.
 *
 * Shape kept in sync with the voice-agent runtime:
 *   { tts_voice_id?: string, speaking_rate?: number, stt_language?: string }
 * An empty TTS voice id means "use the provider default voice".
 */
export default function VoiceSettingsForm({ value, onChange, error }) {
  const settings = {
    tts_voice_id: '',
    speaking_rate: 1.0,
    stt_language: 'en',
    ...(value || {}),
  };

  function update(patch) {
    onChange({ ...settings, ...patch });
  }

  return (
    <div className="vsf">
      {error && <div className="banner banner-error">{error}</div>}

      <div className="field">
        <label htmlFor="vs-voice">TTS voice ID</label>
        <input
          id="vs-voice"
          type="text"
          value={settings.tts_voice_id || ''}
          placeholder="Leave blank to use the provider's default voice"
          onChange={(e) => update({ tts_voice_id: e.target.value })}
        />
        <p className="hint">
          The speech engine's voice identifier. If you are not sure, leave this blank — the platform picks a clear
          natural voice for you.
        </p>
      </div>

      <div className="field">
        <label htmlFor="vs-rate">Speaking rate</label>
        <input
          id="vs-rate"
          type="number"
          min="0.5"
          max="2"
          step="0.05"
          value={settings.speaking_rate}
          onChange={(e) => {
            const v = Number(e.target.value);
            update({ speaking_rate: e.target.value === '' ? '' : v });
          }}
        />
        <p className="hint">1.0 is normal speed. 0.9 is slightly slower and clearer; 1.2 is brisk.</p>
      </div>

      <div className="field">
        <label htmlFor="vs-lang">Speech recognition language</label>
        <select
          id="vs-lang"
          value={settings.stt_language || 'en'}
          onChange={(e) => update({ stt_language: e.target.value })}
        >
          {LANGUAGES.map((l) => (
            <option key={l.value} value={l.value}>
              {l.label}
            </option>
          ))}
        </select>
        <p className="hint">This phase supports English only; Indian English variants help with accents.</p>
      </div>
    </div>
  );
}

/** Fill provider-safe defaults for anything the user left blank. */
export function normalizeVoiceSettings(value) {
  const s = value || {};
  const rate = typeof s.speaking_rate === 'number' && !Number.isNaN(s.speaking_rate) ? s.speaking_rate : 1.0;
  const out = {
    speaking_rate: Math.min(2, Math.max(0.5, rate)),
    stt_language: s.stt_language || 'en',
  };
  const voice = String(s.tts_voice_id || '').trim();
  if (voice) out.tts_voice_id = voice;
  return out;
}
