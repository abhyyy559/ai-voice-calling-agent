import React from 'react';

const LANGUAGES = [
  { value: 'en', label: 'English (en)' },
  { value: 'en-IN', label: 'English — India (en-IN)' },
  { value: 'en-US', label: 'English — US (en-US)' },
];

/**
 * Curated Cartesia English voices (sonic family, verified preset IDs from
 * docs.cartesia.ai). Written to voice_settings.tts_voice_id; an empty value
 * means "use the provider default voice".
 */
export const VOICE_PRESETS = [
  {
    id: '',
    name: 'Platform default',
    detail: 'Let Echo Sarathi pick a clear natural voice',
  },
  {
    id: 'f786b574-daa5-4673-aa0c-cbe3e8534c02',
    name: 'Katie',
    detail: 'US female · stable & realistic (recommended for agents)',
  },
  {
    id: 'a0e99841-438c-4a64-b679-ae501e7d6091',
    name: 'Sarah',
    detail: 'US female · clear & professional',
  },
  {
    id: 'db6b0ed5-d5d3-463d-ae85-518a07d3c2b4',
    name: 'Skylar',
    detail: 'US female · friendly guide tone',
  },
  {
    id: 'a5136bf9-224c-4d76-b823-52bd5efcffcc',
    name: 'Jameson',
    detail: 'US male · warm & steady',
  },
  {
    id: '228fca29-3a0a-435c-8728-5cb483251068',
    name: 'Kiefer',
    detail: 'US male · calm announcer',
  },
  {
    id: '62ae83ad-4f6a-430b-af41-a9bede9286ca',
    name: 'Gemma',
    detail: 'UK female · polished British accent',
  },
  {
    id: 'ef191366-f52f-447a-a398-ed8c0f2943a1',
    name: 'Archie',
    detail: 'UK male · confident British accent',
  },
  {
    id: '6ccbfb76-1fc6-48f7-b71d-91ac6298247b',
    name: 'Tessa',
    detail: 'US female · expressive & emotive',
  },
];

/** LLM choices saved to voice_settings.llm_model ('' = platform default). */
export const LLM_MODEL_CHOICES = [
  { value: '', label: 'Platform default (fast)' },
  {
    value: 'qwen/qwen3.6-27b',
    label: 'Qwen 3.6 27B — recommended · fastest responses',
  },
  {
    value: 'openai/gpt-oss-120b',
    label: 'GPT-OSS 120B — strongest reasoning',
  },
];

/**
 * Voice settings form.
 *
 * Shape kept in sync with the voice-agent runtime:
 *   { tts_voice_id?: string, speaking_rate?: number, stt_language?: string,
 *     llm_model?: string }
 * An empty TTS voice id / llm model means "use the platform default".
 */
export default function VoiceSettingsForm({ value, onChange, error }) {
  const settings = {
    tts_voice_id: '',
    speaking_rate: 1.0,
    stt_language: 'en',
    llm_model: '',
    ...(value || {}),
  };

  const knownVoice = VOICE_PRESETS.some((p) => p.id === (settings.tts_voice_id || ''));
  const [showCustomVoice, setShowCustomVoice] = React.useState(false);
  const customInputVisible =
    showCustomVoice || (!knownVoice && Boolean(settings.tts_voice_id));

  function update(patch) {
    onChange({ ...settings, ...patch });
  }

  return (
    <div className="vsf">
      {error && <div className="banner banner-error">{error}</div>}

      <div className="field">
        <label htmlFor="vs-voice">Voice</label>
        <select
          id="vs-voice"
          value={customInputVisible && !knownVoice ? settings.tts_voice_id : settings.tts_voice_id || ''}
          onChange={(e) => {
            const v = e.target.value;
            if (v === '__custom__') {
              setShowCustomVoice(true);
              return;
            }
            setShowCustomVoice(false);
            update({ tts_voice_id: v });
          }}
        >
          {!knownVoice && settings.tts_voice_id && (
            <option value={settings.tts_voice_id}>Custom voice…</option>
          )}
          {VOICE_PRESETS.map((p) => (
            <option key={p.id || 'default'} value={p.id}>
              {p.name}
            </option>
          ))}
          <option value="__custom__">Custom voice ID…</option>
        </select>
        <p className="hint">
          {(() => {
            const preset = VOICE_PRESETS.find((p) => p.id === (settings.tts_voice_id || ''));
            if (preset) return preset.detail;
            return 'Paste any Cartesia voice ID below.';
          })()}
        </p>
        {customInputVisible && (
          <input
            type="text"
            aria-label="Custom TTS voice ID"
            placeholder="Cartesia voice ID (UUID)"
            value={settings.tts_voice_id || ''}
            onChange={(e) => update({ tts_voice_id: e.target.value })}
            style={{ marginTop: 8 }}
          />
        )}
      </div>

      <div className="field">
        <label htmlFor="vs-model">Conversation model</label>
        <select
          id="vs-model"
          value={settings.llm_model || ''}
          onChange={(e) => update({ llm_model: e.target.value })}
        >
          {LLM_MODEL_CHOICES.map((m) => (
            <option key={m.value || 'default'} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
        <p className="hint">
          Powers how the agent understands replies. The fast default keeps call latency low; switch models only if
          answers feel too simple.
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
        <label htmlFor="vs-prondict">Pronunciation dictionary ID (optional)</label>
        <input
          id="vs-prondict"
          type="text"
          value={settings.pronunciation_dict_id || ''}
          placeholder="e.g. pdict_123abc"
          onChange={(e) => update({ pronunciation_dict_id: e.target.value })}
        />
        <p className="hint">
          Cartesia dictionary for hard-to-pronounce names. Leave blank to use the platform default, if configured.
        </p>
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
  if (voice && voice !== '__custom__') out.tts_voice_id = voice;
  const pron = String(s.pronunciation_dict_id || '').trim();
  if (pron) out.pronunciation_dict_id = pron;
  const model = String(s.llm_model || '').trim();
  if (model) out.llm_model = model;
  return out;
}
