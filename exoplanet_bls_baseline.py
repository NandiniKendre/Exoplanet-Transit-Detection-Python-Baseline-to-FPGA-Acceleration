"""
Exoplanet Transit Detection: BLS-Style Research Baseline
-------------------------------------------------------
Purpose:
1. Generate a synthetic stellar light curve.
2. Inject a repeating, transit-like brightness dip.
3. Search trial periods and transit durations.
4. Estimate the best period and transit depth.
5. Save the data, search results, and baseline metrics.

NOTE:
This is an educational, simplified BLS-style implementation.
Validate against a trusted implementation before scientific claims.
"""

import csv
import math
import random
import time
from pathlib import Path

import numpy as np

try:
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


# ============================================================
# 1. CONFIGURATION
# ============================================================

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = Path("exoplanet_bls_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Synthetic test parameters (known ground truth)
TRUE_PERIOD = 3.70       # days
TRUE_EPOCH = 1.20        # days
TRUE_DURATION = 0.12     # days
TRUE_DEPTH = 0.010       # 1% drop in brightness
NOISE_STD = 0.003

OBSERVATION_SPAN = 27.0  # days
CADENCE = 0.02           # days

# Search configuration
MIN_PERIOD = 2.0
MAX_PERIOD = 6.0
NUM_PERIODS = 400

# Candidate transit durations to test, in days
DURATIONS = [0.06, 0.10, 0.12, 0.16, 0.20]


# ============================================================
# 2. GENERATE SYNTHETIC LIGHT CURVE
# ============================================================

def generate_light_curve():
    """Create normalized stellar flux with an injected transit."""

    time_days = np.arange(
        0.0, OBSERVATION_SPAN, CADENCE, dtype=np.float64
    )

    flux = np.ones_like(time_days)

    # Distance from the center of the nearest transit
    phase_time = (
        (time_days - TRUE_EPOCH + TRUE_PERIOD / 2)
        % TRUE_PERIOD
    ) - TRUE_PERIOD / 2

    in_transit = np.abs(phase_time) <= TRUE_DURATION / 2

    # Inject a box-shaped transit
    flux[in_transit] -= TRUE_DEPTH

    # Add measurement noise
    flux += np.random.normal(0.0, NOISE_STD, len(flux))

    return time_days, flux


# ============================================================
# 3. SIMPLIFIED BLS-STYLE PERIOD SEARCH
# ============================================================

def search_bls(time_days, flux, periods, durations):
    """
    Search trial periods and transit durations.

    For each period:
      - Fold observations into phase.
      - Sort observations by phase.
      - Test transit windows using cumulative sums.
      - Score the brightness difference between inside/outside.

    Score = n_in * n_out / n_total * depth**2

    This is a simplified box-model improvement score,
    not a complete reproduction of every BLS convention.
    """

    n = len(flux)
    flux_mean = np.mean(flux)
    centered_flux = flux - flux_mean

    # Normalize score against overall scatter for interpretability
    variance = np.var(centered_flux)
    if variance <= 0:
        raise ValueError("Flux has zero variance.")

    best = None
    results = []

    for period in periods:

        # Phase in [0, 1)
        phase = (time_days % period) / period

        order = np.argsort(phase)
        sorted_phase = phase[order]
        sorted_flux = centered_flux[order]

        # Duplicate the folded cycle to handle windows crossing phase 1
        phase_extended = np.concatenate(
            [sorted_phase, sorted_phase + 1.0]
        )
        flux_extended = np.concatenate(
            [sorted_flux, sorted_flux]
        )

        cumulative = np.concatenate(
            [[0.0], np.cumsum(flux_extended)]
        )

        for duration in durations:
            q = duration / period

            # Start a candidate window at each observed phase.
            # Prefix sums make each window evaluation efficient.
            for i in range(n):

                j = int(np.searchsorted(
                    phase_extended, sorted_phase[i] + q,
                    side="left"
                ))

                n_in = j - i
                n_out = n - n_in

                # Require sufficient samples inside and outside
                if n_in < 3 or n_out < 10 or n_in >= n:
                    continue

                sum_in = cumulative[j] - cumulative[i]

                # The flux is centered, so its total is approximately zero.
                mean_in = sum_in / n_in
                mean_out = -sum_in / n_out

                depth = mean_out - mean_in

                # Positive depth means a dimming event.
                if depth <= 0:
                    continue

                score = (
                    n_in * n_out / n * depth**2 / variance
                )

                row = {
                    "period_days": float(period),
                    "duration_days": float(duration),
                    "depth": float(depth),
                    "score": float(score),
                    "transit_phase": float(sorted_phase[i]),
                    "samples_in_transit": int(n_in),
                }

                results.append(row)

                if best is None or score > best["score"]:
                    best = row.copy()

    return best, results


# ============================================================
# 4. SAVE CSV FILES
# ============================================================

def save_csv(path, rows):
    if not rows:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# 5. RUN EXPERIMENT
# ============================================================

print("=" * 60)
print("EXOPLANET TRANSIT DETECTION — BLS-STYLE BASELINE")
print("=" * 60)

time_days, flux = generate_light_curve()

periods = np.linspace(
    MIN_PERIOD, MAX_PERIOD, NUM_PERIODS
)

print(f"Number of observations: {len(time_days)}")
print(f"Observation span: {OBSERVATION_SPAN:.2f} days")
print(f"Trial periods: {len(periods)}")
print(f"Trial durations: {len(DURATIONS)}")
print("Running period search...")

start = time.perf_counter()

best, search_results = search_bls(
    time_days, flux, periods, DURATIONS
)

elapsed_seconds = time.perf_counter() - start

if best is None:
    raise RuntimeError(
        "No candidate found. Adjust the search settings."
    )


# ============================================================
# 6. REPORT RESULTS
# ============================================================

period_error = abs(best["period_days"] - TRUE_PERIOD)

print("\nKNOWN INJECTED SIGNAL")
print(f"True period:       {TRUE_PERIOD:.5f} days")
print(f"True duration:     {TRUE_DURATION:.5f} days")
print(f"True transit depth:{TRUE_DEPTH:.5f}")

print("\nBEST DETECTED CANDIDATE")
print(f"Detected period:   {best['period_days']:.5f} days")
print(f"Detected duration: {best['duration_days']:.5f} days")
print(f"Estimated depth:   {best['depth']:.5f}")
print(f"Detection score:   {best['score']:.5f}")
print(f"Period error:      {period_error:.5f} days")
print(f"Search runtime:    {elapsed_seconds:.4f} seconds")


# ============================================================
# 7. SAVE REPRODUCIBLE OUTPUTS
# ============================================================

light_curve_rows = [
    {"time_days": float(t), "normalized_flux": float(f)}
    for t, f in zip(time_days, flux)
]

save_csv(
    OUTPUT_DIR / "synthetic_light_curve.csv",
    light_curve_rows
)

save_csv(
    OUTPUT_DIR / "bls_search_results.csv",
    search_results
)

metrics = [
    {"metric": "seed", "value": SEED},
    {"metric": "observations", "value": len(time_days)},
    {"metric": "true_period_days", "value": TRUE_PERIOD},
    {"metric": "detected_period_days", "value": best["period_days"]},
    {"metric": "absolute_period_error_days", "value": period_error},
    {"metric": "true_depth", "value": TRUE_DEPTH},
    {"metric": "estimated_depth", "value": best["depth"]},
    {"metric": "best_score", "value": best["score"]},
    {"metric": "runtime_seconds", "value": elapsed_seconds},
    {"metric": "number_of_trial_periods", "value": len(periods)},
    {"metric": "number_of_durations", "value": len(DURATIONS)},
]

save_csv(OUTPUT_DIR / "baseline_metrics.csv", metrics)

print(f"\nOutput files saved in: {OUTPUT_DIR.resolve()}")


# ============================================================
# 8. OPTIONAL PLOTS
# ============================================================

if PLOTTING_AVAILABLE:

    # Light curve
    plt.figure(figsize=(12, 4))
    plt.plot(time_days, flux, ".", markersize=2)
    plt.xlabel("Time (days)")
    plt.ylabel("Normalized flux")
    plt.title("Synthetic light curve with injected transit")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "light_curve.png", dpi=160)
    plt.show()

    # Period score
    scores_by_period = {}

    for row in search_results:
        p = row["period_days"]
        scores_by_period[p] = max(
            scores_by_period.get(p, 0.0),
            row["score"]
        )

    x = np.array(sorted(scores_by_period))
    y = np.array([scores_by_period[p] for p in x])

    plt.figure(figsize=(10, 4))
    plt.plot(x, y)
    plt.axvline(
        TRUE_PERIOD, linestyle="--",
        label="Injected period"
    )
    plt.xlabel("Trial period (days)")
    plt.ylabel("Best transit-window score")
    plt.title("BLS-style period search")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "periodogram.png", dpi=160)
    plt.show()

print("\nExperiment complete.")