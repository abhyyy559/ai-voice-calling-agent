"""G.711 mu-law helpers for the Twilio media bridge (stdlib audioop)."""
from __future__ import annotations

import audioop


def ulaw_to_pcm16(data: bytes) -> bytes:
    """Decode 8 kHz mu-law to 16-bit little-endian PCM (2 bytes per sample)."""
    return audioop.ulaw2lin(data, 2)


def pcm16_to_ulaw(data: bytes) -> bytes:
    """Encode 16-bit little-endian PCM to 8 kHz mu-law (1 byte per sample)."""
    return audioop.lin2ulaw(data, 2)


def downsample_pcm16(data: bytes, factor: int = 6) -> bytes:
    """Decimate 16-bit LE PCM per SAMPLE, keeping every `factor`-th sample
    (48k -> 8k uses factor=6).

    Output length is ``ceil(n_samples / factor) * 2`` bytes. Aliasing is
    acceptable for v1 speech.
    """
    if factor <= 1:
        return data
    step = 2 * factor
    return b"".join(data[i : i + 2] for i in range(0, len(data) - 1, step))
