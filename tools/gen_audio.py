#!/usr/bin/env python3
"""Generate ONE LINE's original sound effects as small WAV files.

All SFX are simple synthesized tones with short envelopes — 100% original,
generated procedurally with only the Python standard library. See
docs/THIRD_PARTY_LICENSES.md. Run:

    python3 tools/gen_audio.py [--out assets/audio]
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import wave

SAMPLE_RATE = 44100


def _tone(freq: float, dur: float, volume: float = 0.4, decay: float = 8.0,
          freq_end: float | None = None) -> list:
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        f = freq if freq_end is None else freq + (freq_end - freq) * (i / max(1, n))
        env = math.exp(-decay * t)  # quick percussive decay
        s = math.sin(2 * math.pi * f * t) * env * volume
        samples.append(s)
    return samples


def _chord(freqs, dur, volume=0.3, decay=6.0) -> list:
    layers = [_tone(f, dur, volume, decay) for f in freqs]
    n = max(len(l) for l in layers)
    mixed = [0.0] * n
    for layer in layers:
        for i, s in enumerate(layer):
            mixed[i] += s / len(layers)
    return mixed


def _write_wav(path: str, samples: list) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in samples:
            v = int(max(-1.0, min(1.0, s)) * 32767)
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


def build(out_dir: str) -> None:
    effects = {
        "node": _tone(660, 0.09, 0.35, 12.0),
        "connect": _tone(520, 0.10, 0.35, 9.0, freq_end=700),
        "invalid": _tone(160, 0.14, 0.35, 7.0, freq_end=120),
        "button": _tone(440, 0.06, 0.25, 14.0),
        "complete": _chord([523, 659, 784], 0.55, 0.35, 4.0),  # C-E-G major
    }
    for name, samples in effects.items():
        path = os.path.join(out_dir, f"{name}.wav")
        _write_wav(path, samples)
        print(f"wrote {path} ({len(samples)} samples)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate ONE LINE SFX.")
    parser.add_argument("--out", default="assets/audio")
    args = parser.parse_args()
    build(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
