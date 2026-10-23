# Recording Guide — Getting Clean Chenda Strikes for PGSD

This guide explains how to record Chenda strikes that will give
R² > 0.80 when analysed by PGSD.

---

## Why recording quality matters

PGSD models the drum as a sum of 18 decaying sinusoids. For R² to be high,
the recording must contain:
1. A single clean membrane strike (not a performance)
2. At least 2–3 seconds of clean decay after the strike
3. Minimal background noise and room reverb

A YouTube performance recording gives R² ≈ 0.07 because it contains
multiple instruments, crowd noise, and overlapping strikes. A single
clean strike in a quiet room gives R² ≈ 0.85–0.95.

---

## Equipment

You do not need professional equipment. A smartphone works fine.

| Equipment | Acceptable | Not acceptable |
|-----------|-----------|----------------|
| Phone mic (Voice Memos, etc.) | ✓ | |
| External USB mic | ✓ | |
| Field recorder (Zoom H1, etc.) | ✓ | |
| Bluetooth microphone | | ✗ (compression) |
| Phone on speakerphone call | | ✗ (codec artifacts) |

---

## Recording conditions

**Room:**
- Quiet room with some soft furnishings (not a tiled bathroom)
- No fans, AC units, or traffic noise
- Close doors and windows

**Microphone placement:**
- 20–40 cm from the striking face of the drum
- Slightly off-axis (not dead centre) — avoids air blast from the strike
- Consistent position across all recordings

**Strike technique:**
- Strike the drum once
- Let it ring fully — at least 3 seconds of silence after the strike
- Do not muffle or touch the membrane after striking
- Strike firmly enough to get a clean onset (SNR > 20 dB)

---

## Ideal recording set for the paper

Record each of these as a separate file:

| Filename | Strike position | Tension | Notes |
|----------|----------------|---------|-------|
| `strike_centre.wav` | Centre (0R) | Normal | |
| `strike_mid.wav` | Mid-radius (~6 cm) | Normal | Most informative for T2 |
| `strike_near_rim.wav` | Near rim (~10 cm) | Normal | |
| `strike_tight.wav` | Mid-radius | Tight skin | For T1 comparison |
| `strike_worn.wav` | Mid-radius | Worn skin | For T3 comparison |

This set gives ground truth for Tasks 1, 2, and 3 simultaneously.

---

## Quality check before running PGSD

Run the inspector notebook first:

```bash
jupyter notebook notebooks/recording_inspector.ipynb
```

It checks:

| Metric | Good | Acceptable | Bad |
|--------|------|-----------|-----|
| SNR | > 25 dB | 15–25 dB | < 15 dB |
| T60 estimate | 0.5–3.0 s | 3–5 s | > 5 s |
| f₁ detected | 100–220 Hz | — | Not found |
| Energy flatness | < 0.2 | 0.2–0.5 | > 0.5 |
| Strikes detected | 1 | 2–3 | > 3 |

If any metric shows **Bad**, re-record before running PGSD.

---

## Placing recordings in the repo

Copy your WAV files into:
```
audio/real_recordings/
```

Name them descriptively:
```
audio/real_recordings/chenda_centre_strike.wav
audio/real_recordings/chenda_mid_strike.wav
audio/real_recordings/chenda_rim_strike.wav
```

Then run:
```bash
jupyter notebook notebooks/real_recordings_analysis.ipynb
```

Set `AUDIO_DATASET = "audio/real_recordings"` in Cell 1.

---

## Interpreting R² results

| R² | Meaning | Action |
|----|---------|--------|
| > 0.85 | Excellent — physics model fits well | Include in paper |
| 0.70–0.85 | Good — some model-reality gap (expected) | Include, note gap |
| 0.50–0.70 | Acceptable — check for background noise | Optional |
| < 0.50 | Poor — re-record | Do not include |

The model-reality gap (R² < 1.0 on real recordings) is expected and
honest. The Rayleigh damping model captures the dominant decay but
not boundary reflections, non-linear contact mechanics, or shell
resonance. R² ≈ 0.80 on a real recording is a strong result.
