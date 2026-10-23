# Implementation Notes: Pitfalls Fixed in PGSD v3

This document records the five bugs identified and fixed between PGSD v1
and v3. Each bug caused a silent, catastrophic failure in an otherwise
correct physics model. They are documented here for reproducibility.

---

## Bug 1 — Chebyshev grid direction

**Location:** `src/chenda_spectral.py` → `_fix_grid()`

**Symptom:** Mode shapes were evaluated at the wrong radial positions,
causing physically incorrect amplitude patterns. Strike position recovery
was random (43%R error instead of 0.3%R).

**Cause:** Chebyshev nodes descend from r ≈ 0.998 to r ≈ 0.063.
`RegularGridInterpolator` requires ascending axes. The grid was passed
in descending order, inverting the radial coordinate silently.

**Fix:** Flip r_cheb and the corresponding rows of all mode arrays
before interpolation:
```python
r_asc   = r_cheb[::-1].copy()
psi_asc = psi_raw[::-1, :].copy()
```

---

## Bug 2 — Missing centre point

**Symptom:** Centre strikes (r = 0) produced near-zero amplitude for all
modes, making them indistinguishable from rim strikes.

**Cause:** The Chebyshev grid excludes r = 0 by construction.
`RegularGridInterpolator` with `fill_value=0` returned zero for any
query at r = 0.

**Fix:** Extend the grid to r = 0 via linear extrapolation from the two
innermost Chebyshev nodes:
```python
r0, r1 = r_asc[0], r_asc[1]
v0, v1 = psi_asc[0, :], psi_asc[1, :]
v_centre = v0 - r0 * (v1 - v0) / (r1 - r0)
r_full = np.concatenate([[0.0], r_asc])
psi_full = np.vstack([v_centre[None, :], psi_asc])
```

---

## Bug 3 — Degenerate pair excitation

**Symptom:** Strike position recovery produced nearly flat correlation
curves — all positions gave similar match quality.

**Cause:** For degenerate mode pairs (cos(mθ)/sin(mθ) in symmetric
geometries), the combined excitation sqrt(Ψ_A² + Ψ_B²) is approximately
constant in θ, collapsing all angular information and flattening the
radial excitation pattern.

**Fix:** Use signal-level template matching instead of coefficient
correlation. Synthesise a full noiseless template at each candidate r_s
and correlate directly with the observed signal:
```python
r_est = argmax_r  dot(x_hat(r), x) / (||x_hat(r)|| * ||x||)
```
This evaluates the full 18-mode superposition, including the combined
degenerate pair effect, rather than individual coefficients.

---

## Bug 4 — Shape-dependent bandpass filter (Task 3)

**Symptom (4a):** T60 for the Hourglass was measured at Cylinder's f₁
(127.8 Hz) instead of Hourglass f₁ (201.2 Hz), underestimating decay
and producing wrong CI values.

**Symptom (4b):** T60 fit ran to t = 0.9×duration, including the noise
floor. For fast-decaying shapes (Hourglass T60 < 1s), the noise floor
dominated the fit tail, inverting the CI for worn skin.

**Fix (4a):** Use shape-specific f₁ from the eigensolver:
```python
f_centre = freqs_hz[0]   # shape-specific, not hardcoded
```

**Fix (4b):** Gate the envelope fit to samples above 2× the noise floor:
```python
noise_floor = env_smooth.max() / 31.6   # -30 dB
above = np.where(env_smooth > noise_floor * 2)[0]
i0, i1 = above[0], above[-1]
```

---

## Bug 5 — Ridge regularisation scale

**Symptom:** At tensions far from T_ref, the basis matrix Φ became
ill-conditioned and the fixed λ = 1e-6 over-regularised, suppressing
real modal content and producing near-zero coefficients.

**Cause:** λ = 1e-6 is appropriate when ||Φ^T Φ||_F ≈ 1. When frequencies
shift significantly, the Gram matrix norm changes by 2–3 orders of magnitude,
making the fixed λ either too large (over-regularise) or too small
(under-regularise).

**Fix:** Scale λ by the Frobenius norm of the Gram matrix:
```python
G   = Phi.T @ Phi
lam = rel_lam * np.linalg.norm(G, 'fro')   # rel_lam = 1e-6
c   = np.linalg.solve(G + lam*np.eye(N), Phi.T @ x)
```
This ensures consistent regularisation regardless of signal scale or
tension offset.

---

## Note — f₁ clamp and damping are experiment-specific

**Location:** `src/chenda_pgsd_v3.py` → `pgsd_refine()`, `set_experiment_mode()`

Real recordings use an f₁ clamp of 150–280 Hz and η₁ = 1.087. Synthetic
Cylinder and Oval shells have f₁ ≈ 110–138 Hz (Table 1), so the clamp must
stay off for them, and synthetic experiments use η₁ = 0.80.

- `pgsd_refine(..., f1_min=None, f1_max=None)` is the default (no clamp).
- `set_experiment_mode("synthetic")` or `("real")` selects η₁.
- The basis cache key includes the damping parameters.
