"""G.711 mu-law <-> 16-bit linear PCM conversion.

Pure-Python table-based implementation of the classic Sun Microsystems
``g711.c`` reference algorithm (the same pairing the stdlib ``audioop`` module
used).  Python 3.13 removed ``audioop``, so we must NOT import it; instead the
256-entry decode table and the 65536-entry encode table are built once at
import time.

Conventions:
- PCM is signed little-endian 16-bit ("pcm_s16le"), 8 kHz.
- mu-law bytes are the standard 8-bit companded codes used by Twilio Media
  Streams (G.711 u-law, 8 kHz).

Note: the primary pipeline never converts audio -- Twilio mu-law goes to
Deepgram raw, and Cartesia is asked for pcm_mulaw@8000 directly.  This module
exists for the fallback path (pcm_s16le responses) and for tests.
"""

from __future__ import annotations

# Decode-side constants (16-bit domain).
_BIAS = 0x84  # 132
_SIGN_BIT = 0x80
_QUANT_MASK = 0x0F
_SEG_MASK = 0x70
_SEG_SHIFT = 4

# Encode-side constants (14-bit domain, as in g711.c's st_14linear2ulaw).
_CLIP_14 = 8159
_BIAS_14 = _BIAS >> 2  # 33
_SEG_UEND = (0x3F, 0x7F, 0xFF, 0x1FF, 0x3FF, 0x7FF, 0xFFF, 0x1FFF)


def _ulaw_to_linear(u_val: int) -> int:
    """Decode one mu-law byte to a 16-bit linear PCM sample (g711.c)."""
    u_val = ~u_val & 0xFF
    t = ((u_val & _QUANT_MASK) << 3) + _BIAS
    t <<= (u_val & _SEG_MASK) >> _SEG_SHIFT
    return (_BIAS - t) if (u_val & _SIGN_BIT) else (t - _BIAS)


def _linear_to_ulaw(pcm_val: int) -> int:
    """Encode one 16-bit linear PCM sample to a mu-law byte (g711.c)."""
    pcm_val >>= 2  # 16-bit -> 14-bit domain
    if pcm_val < 0:
        pcm_val = -pcm_val
        mask = 0x7F
    else:
        mask = 0xFF
    if pcm_val > _CLIP_14:
        pcm_val = _CLIP_14
    pcm_val += _BIAS_14
    seg = 8
    for i, end in enumerate(_SEG_UEND):
        if pcm_val <= end:
            seg = i
            break
    if seg >= 8:  # out of range: return maximum magnitude code
        return 0x7F ^ mask
    uval = (seg << 4) | ((pcm_val >> (seg + 3)) & 0x0F)
    return uval ^ mask


# Precomputed lookup tables, built once at import time.
MULAW_TO_PCM16: tuple[int, ...] = tuple(_ulaw_to_linear(b) for b in range(256))
PCM16_TO_MULAW: bytes = bytes(
    _linear_to_ulaw(v) for v in range(-32768, 32768)
)

# mu-law silence byte: MULAW_TO_PCM16[0xFF] == 0. (0x7F, the "negative zero"
# code, also decodes to 0; we pad with 0xFF by convention.)
MULAW_SILENCE = 0xFF


def mulaw_bytes_to_pcm16(data: bytes) -> bytes:
    """Convert a block of mu-law bytes to little-endian signed 16-bit PCM."""
    out = bytearray(len(data) * 2)
    for i, b in enumerate(data):
        out[2 * i] = MULAW_TO_PCM16[b] & 0xFF
        out[2 * i + 1] = (MULAW_TO_PCM16[b] >> 8) & 0xFF
    return bytes(out)


def pcm16_bytes_to_mulaw(data: bytes) -> bytes:
    """Convert little-endian signed 16-bit PCM to mu-law bytes.

    A trailing odd byte (incomplete sample) is ignored.
    """
    n = len(data) - (len(data) % 2)
    return bytes(
        PCM16_TO_MULAW[
            int.from_bytes(data[i:i + 2], "little", signed=True) + 32768
        ]
        for i in range(0, n, 2)
    )
