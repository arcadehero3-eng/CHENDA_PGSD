# Notebooks

| Notebook | Paper section |
|---|---|
| `chenda_pgsd_analysis.ipynb` | Sec. 4.3: PGSD vs FFT, sinusoidal and NMF on real recordings (Table 5) |
| `real_recordings_analysis.ipynb` | per-strike analysis of the raw centre / edge / hand strikes |
| `recording_inspector.ipynb` | inspect a single recording: spectrum, decay, fitted modes |
| `fft_synthesis_baseline.ipynb` | FFT-based synthesis baseline |
| `cnn_baseline.ipynb` | supervised CNN baseline on synthetic strikes |

The notebooks were run on Kaggle. To run them locally, change the path cell at the top:

- audio: `audio/real_recordings/` in this repository
- model code: `src/chenda_pgsd_v3.py` and `src/chenda_spectral.py`

For real recordings, call `set_experiment_mode("real")` and pass `f1_min=150.0, f1_max=280.0` to `pgsd_refine`.
