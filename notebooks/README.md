# Notebooks

| Notebook | Paper section |
|---|---|
| `chenda_pgsd_analysis.ipynb` | Sec. 4.3: PGSD vs FFT, sinusoidal and NMF on real recordings (Table 5) |
| `real_recordings_analysis.ipynb` | per-strike analysis of the raw centre / edge / hand strikes |
| `recording_inspector.ipynb` | inspect a single recording: spectrum, decay, fitted modes |
| `fft_synthesis_baseline.ipynb` | FFT-based synthesis baseline |
| `cnn_baseline.ipynb` | supervised CNN baseline on synthetic strikes (needs `pip install torch`) |

## Running

**Locally:** start Jupyter from the repository and open a notebook from this folder. No path edits are needed.
The first cell finds the repository, loads the model from `src/` and reads audio from `audio/`.
Outputs go to `outputs/<notebook name>/`.

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

**On Kaggle:** clone the repository into the working directory first, then run all cells:

```python
!git clone https://github.com/arcadehero3-eng/CHENDA_PGSD.git /kaggle/working/CHENDA_PGSD
```

If the repository lives somewhere else, set the `CHENDA_REPO` environment variable to its path.
