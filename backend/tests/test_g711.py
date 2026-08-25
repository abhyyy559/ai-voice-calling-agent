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


def test_downsample_factor6_keeps_every_6th_sample():
    # 1024 samples, sample k encodes value k (LE 16-bit)
    pcm = b"".join(k.to_bytes(2, "little") for k in range(1024))
    out = downsample_pcm16(pcm, 6)
    expected_samples = ((1024 + 5) // 6) * 2  # ceil(1024/6) samples -> bytes
    assert len(out) == expected_samples
    first = int.from_bytes(out[0:2], "little")
    second = int.from_bytes(out[2:4], "little")
    assert (first, second) == (0, 6)


def test_downsample_default_is_6():
    pcm = b"".join(k.to_bytes(2, "little") for k in range(12))
    assert downsample_pcm16(pcm) == downsample_pcm16(pcm, 6)
