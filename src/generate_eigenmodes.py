"""
generate_eigenmodes.py
======================
Generate 2-row x 5-column eigenmode figures for Cylinder, Hourglass, and
Oval Chenda shell geometries.

  - White background, clean publication style
  - 10 unique modes per figure  (degenerate pairs de-duplicated)
  - Nodal lines drawn as thin black contour at Z=0
  - Colourbar centred above the grid
  - Labels use italic math subscripts matching the paper

Usage
-----
    python generate_eigenmodes.py

Output (same directory as this script)
-------
    eigenmodes_cylinder.png
    eigenmodes_hourglass.png
    eigenmodes_oval.png

Requirements
------------
    numpy, matplotlib, scipy
    chenda_spectral.py  (same directory)
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, Normalize
from matplotlib.cm import ScalarMappable
from scipy.interpolate import RegularGridInterpolator

# ── locate chenda_spectral.py ─────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

_src = open(os.path.join(SCRIPT_DIR, 'chenda_spectral.py')).read()
_g   = {'__file__': os.path.join(SCRIPT_DIR, 'chenda_spectral.py')}
exec(compile(_src[:_src.rfind('\nif __name__')], 'chenda_spectral', 'exec'), _g)

solve_eigenmodes = _g['solve_eigenmodes']
SHAPES           = _g['SHAPES']

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — edit here
# ─────────────────────────────────────────────────────────────────────────────
T            = 3500.0   # membrane tension (N/m)
R_PHYS       = 0.125    # membrane radius (m)
SIGMA_MEM    = 1.4      # reference surface density (kg/m²)
NR           = 25       # Chebyshev radial nodes
NTH          = 24       # Fourier angular nodes
N_UNIQUE     = 10       # unique modes to show (2 rows × 5 cols)
DUP_THRESH   = 2.0      # Hz — modes closer than this are treated as duplicates
N_DISP_R     = 200      # radial points on display polar grid
N_DISP_TH    = 300      # angular points on display polar grid
DPI          = 180      # output resolution
OUTPUT_DIR   = os.path.join(os.path.dirname(SCRIPT_DIR), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHAPES_TO_PLOT = ['Cylinder', 'Hourglass', 'Oval']
# ─────────────────────────────────────────────────────────────────────────────


def pick_unique_modes(freqs, modes, n_unique, dup_thresh):
    """
    Return the first n_unique modes that are NOT degenerate duplicates.

    A mode is a duplicate when its frequency is within dup_thresh Hz of
    the PREVIOUS kept mode.  This keeps the FIRST of each degenerate pair
    and discards the second — consistent with the paper figures.

    Parameters
    ----------
    freqs     : (M,) array of eigenfrequencies
    modes     : list of M mode arrays
    n_unique  : how many unique modes to return
    dup_thresh: frequency gap below which two modes are considered degenerate

    Returns
    -------
    sel_idx   : list of integer indices into freqs/modes
    """
    sel_idx   = []
    last_freq = -np.inf
    for i, f in enumerate(freqs):
        if f - last_freq > dup_thresh:   # not a duplicate
            sel_idx.append(i)
            last_freq = f
        if len(sel_idx) == n_unique:
            break
    if len(sel_idx) < n_unique:
        raise RuntimeError(
            f"Only {len(sel_idx)} unique modes found; "
            f"request more than {len(freqs)} raw modes.")
    return sel_idx


def prepare_modes(r_cheb, modes_raw, indices):
    """
    Select modes by index, flip to ascending r, extrapolate to r=0.

    The raw Chebyshev grid descends (r[0]≈1, r[-1]≈0.06).
    RegularGridInterpolator requires ascending axes.
    The grid excludes r=0 (clamped boundary), so we linearly extrapolate
    from the two innermost nodes.

    Returns
    -------
    r_full   : (Nr+1,) ascending grid with r=0 prepended
    out_modes: list of (Nr+1, Nth) arrays, one per selected index
    """
    r_asc     = r_cheb[::-1]
    out_modes = []
    for idx in indices:
        m     = modes_raw[idx][::-1, :]          # flip rows to ascending r
        slope = (m[1, :] - m[0, :]) / (r_asc[1] - r_asc[0])
        row0  = m[0, :] - slope * r_asc[0]      # linear extrap → r=0
        out_modes.append(np.vstack([row0[np.newaxis, :], m]))
    r_full = np.concatenate([[0.0], r_asc])
    return r_full, out_modes


# pre-compute shared display grid
r_disp  = np.linspace(0.0, 1.0, N_DISP_R)
th_disp = np.linspace(0.0, 2 * np.pi, N_DISP_TH)
R_D, TH_D = np.meshgrid(r_disp, th_disp)
X_D = R_D * np.cos(TH_D)
Y_D = R_D * np.sin(TH_D)

# boundary ring
_th_ring = np.linspace(0, 2 * np.pi, 400)
_xring   = np.cos(_th_ring)
_yring   = np.sin(_th_ring)


def interpolate_mode(psi, r_full, th_ext):
    """Interpolate one (Nr+1, Nth) mode onto the Cartesian display grid."""
    psi_ext = np.hstack([psi, psi[:, 0:1]])
    interp  = RegularGridInterpolator(
        (r_full, th_ext), psi_ext,
        method='linear', bounds_error=False, fill_value=0.0)
    pts = np.column_stack([R_D.ravel(),
                           TH_D.ravel() % (2 * np.pi)])
    return interp(pts).reshape(N_DISP_TH, N_DISP_R)


def generate_figure(shape_name):
    """Compute, select, and plot 10 unique eigenmodes for one shell shape."""

    cfg = SHAPES[shape_name]
    print(f"  {shape_name}: computing eigenmodes...", end='', flush=True)

    # request enough modes to have N_UNIQUE unique ones even with many pairs
    n_request = N_UNIQUE * 3
    freqs_hz, modes_raw, r_cheb, th, _ = solve_eigenmodes(
        Nr=NR, Nth=NTH,
        density_fn=cfg['density_fn'],
        density_kw=cfg['density_kw'],
        n_modes=n_request,
        R_phys=R_PHYS, T=T, sigma_mem=SIGMA_MEM,
    )

    # select 10 unique (non-degenerate) modes
    sel_idx = pick_unique_modes(freqs_hz, modes_raw, N_UNIQUE, DUP_THRESH)
    sel_freqs = [freqs_hz[i] for i in sel_idx]
    print(f" f1={sel_freqs[0]:.1f} Hz  "
          f"unique modes: {[f'{f:.0f}' for f in sel_freqs]}")

    th_ext = np.append(th, th[0] + 2 * np.pi)
    r_full, modes_prep = prepare_modes(r_cheb, modes_raw, sel_idx)

    # ── figure layout ─────────────────────────────────────────────────────────
    fig, axes = plt.subplots(2, 5, figsize=(18, 8),
                             facecolor='white',
                             gridspec_kw=dict(hspace=0.35, wspace=0.05))
    axes = axes.flatten()

    # ── colourbar strip centred above panels (drawn first) ────────────────────
    cbar_ax = fig.add_axes([0.30, 0.93, 0.40, 0.030])   # [left,bot,w,h]
    sm      = ScalarMappable(cmap='RdBu_r', norm=Normalize(-1, 1))
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_ticks([-1, 0, 1])
    cbar.set_ticklabels(['Inward', 'Nodal', 'Outward'], fontsize=9)
    cbar.ax.xaxis.set_ticks_position('bottom')
    cbar.ax.xaxis.set_label_position('bottom')
    cbar.outline.set_linewidth(0.6)

    # ── title ─────────────────────────────────────────────────────────────────
    fig.text(0.50, 0.99,
             f'Vibrational Eigenmodes: {shape_name} Shell',
             ha='center', va='top',
             fontsize=14, fontweight='bold', color='black')

    # ── plot each mode ─────────────────────────────────────────────────────────
    for panel_idx, (mode_arr, freq) in enumerate(zip(modes_prep, sel_freqs)):
        ax = axes[panel_idx]

        Z    = interpolate_mode(mode_arr, r_full, th_ext)
        vmax = np.abs(Z).max() + 1e-12
        norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

        # filled colour map
        ax.contourf(X_D, Y_D, Z,
                    levels=128, cmap='RdBu_r', norm=norm,
                    antialiased=True)

        # nodal lines (Z = 0)
        ax.contour(X_D, Y_D, Z,
                   levels=[0], colors='black',
                   linewidths=0.8, alpha=0.85)

        # membrane boundary
        ax.plot(_xring, _yring, 'k-', lw=1.2)

        # frequency label — italic subscript matching paper style
        ax.set_title(
            rf'$f_{{{panel_idx + 1}}}$ : {freq:.0f} Hz',
            fontsize=9, color='black', pad=4,
            fontfamily='serif',
        )

        ax.set_aspect('equal')
        ax.set_xlim(-1.12, 1.12)
        ax.set_ylim(-1.12, 1.12)
        ax.axis('off')
        ax.set_facecolor('white')

    # ── save ──────────────────────────────────────────────────────────────────
    plt.subplots_adjust(left=0.01, right=0.99,
                        top=0.88,  bottom=0.02)

    out_path = os.path.join(OUTPUT_DIR,
                            f'eigenmodes_{shape_name.lower()}.png')
    plt.savefig(out_path, dpi=DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  Saved  -> {out_path}")
    return out_path


if __name__ == '__main__':
    print(f"Generating eigenmode figures  T = {T} N/m\n")
    for shape in SHAPES_TO_PLOT:
        generate_figure(shape)
    print('\nDone.')
