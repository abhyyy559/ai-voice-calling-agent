# Task 1 Brief: g711 codec module

**Files:**
- Create: `backend/app/services/g711.py`
- Test: `backend/tests/test_g711.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `ulaw_to_pcm16(data: bytes) -> bytes`, `pcm16_to_ulaw(data: bytes) -> bytes`, `downsample_pcm16(data: bytes, factor: int = 6) -> bytes` — later tasks import these exact names.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_g711.py` with exactly:

```python
"""g711 mu-law codec roundtrips used by the Twilio media bridge."""
from app.services.g711 import downsample_pcm16, pcm16_to_ulaw, ulaw_to_pcm16


def test_roundtrip_silence():
    raw = bytes([0xFF]) * 160  # mu-law silence
    assert len(ulaw_to_pcm16(raw)) == 320
    assert pcm16_to_ulaw(ulaw_to_pcm16(raw))[:160] == raw


def test_roundtrip_tone_lengths():
    pcm = b"\x00\x40" * 320  # tiny positive samples, 20ms @8k
    ulaw = pcm16_to_ulaw(pcm)
    assert len(ulaw) == 320
    back = ulaw_to_pcm16(ulaw)
    assert len(back) == len(pcm)


def test_downsample_factor6():
    pcm = bytes(range(256)) * 8  # 2048 samples
    out = downsample_pcm16(pcm, 6)
    assert len(out) == (2048 // 6) * 2


def test_downsample_default_is_6():
    assert downsample_pcm16(b"\x01\x00" * 12) == downsample_pcm16(b"\x01\x00" * 12, 6)
```

- [ ] **Step 2: Run → expect FAIL**

Run (workdir: `C:\Users\home\OneDrive\Documents\work\projects\ai voice calling agent\backend`):
`.venv\Scripts\python.exe -m pytest tests\test_g711.py -q`
Expected: collection error `No module named 'app.services.g711'`.

- [ ] **Step 3: Implement**

Create `backend/app/services/g711.py` with exactly:

```python
"""G.711 mu-law helpers for the Twilio media bridge (stdlib audioop)."""
from __future__ import annotations

import audioop


def ulaw_to_pcm16(data: bytes) -> bytes:
    """Decode 8 kHz mu-law to 16-bit little-endian PCM (2 bytes per sample)."""
    return audioop.ulaw2lin(data, 2)


def pcm16_to_ulaw(data: bytes) -> bytes:
    """Encode 16-bit little-endian PCM to 8 kHz mu-law (1 byte per sample)."""
    return audioop.lin2ulaw(data)


def downsample_pcm16(data: bytes, factor: int = 6) -> bytes:
    """Naive decimation of 16-bit LE PCM by `factor` (48k->8k uses 6).

    Keeps every `factor`-th sample. Aliasing is acceptable for v1 speech.
    """
    if factor <= 1:
        return data
    return b"".join(data[i : i + 2] for i in range(0, len(data) - 1, 2 * factor))
```

- [ ] **Step 4: Run → PASS**

Same command. Expected: `4 passed`.

- [ ] **Step 5: Report**

Do NOT git add/commit. Write full report to `.superpowers/sdd/t1-report.md`, then return ONLY: status / files / one-line test result / concerns.

## Global Constraints

- Shell is Windows PowerShell 5.1. Do NOT run any git commands.
- Touch ONLY the two files listed above.
