"""
Exoplanet transit detection: simplified BLS-style synthetic baseline.

IMPORTANT:
- This is an educational baseline, not a validated scientific BLS implementation.
- It generates synthetic data and searches a grid of trial periods/durations.
- Validate against a trusted implementation before scientific use.
"""

from pathlib import Path
import time
import numpy as np

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(exist_ok=True)

# Synthetic signal configuration
RANDOM_SEED = 7
N_OBSERVATIONS = 1350
TIME_SPAN_DAYS = 27.0
TRUE_PERIOD = 3.70
TRANSIT_EPOCH = 1.20
TRUE_DURATION = 0.12
TRUE_DEPTH = 0.01
NOISE_STD = 0.003

# Search configuration
PERIOD_MIN = 2.0
PERIOD_MAX = 6.0
NUM_PERIODS = 400
DURATIONS = [0.06, 0.10, 0.12, 0.16, 0.20]


def generate_synthetic_light_curve():
    rng = np.random.default_rng(RANDOM_SEED)
    time_days = np.linspace(0.0, TIME_SPAN_DAYS, N_OBSERVATIONS, endpoint=False)
    flux = 1.0 + rng.normal(0.0, NOISE_STD, size=N_OBSERVATIONS)
    phase_time = ((time_days - TRANSIT_EPOCH + TRUE_PERIOD / 2) % TRUE_PERIOD) - TRUE_PERIOD / 2
    in_transit = np.abs(phase_time) < TRUE_DURATION / 2
    flux[in_transit] -= TRUE_DEPTH
    return time_days, flux


def score_period_duration(time_days, flux, period, duration):
    """Return best simple transit-window score, depth and epoch for one trial."""
    phase = np.mod(time_days, period) / period
    order = np.argsort(phase)
    phase_sorted = phase[order]
    flux_sorted = flux[order]
    n = len(flux_sorted)
    if n < 5:
        return -np.inf, np.nan, np.nan

    # Duplicate phase cycle to allow windows crossing phase=1.
    phase2 = np.concatenate([phase_sorted, phase_sorted + 1.0])
    flux2 = np.concatenate([flux_sorted, flux_sorted])
    prefix = np.concatenate([[0.0], np.cumsum(flux2)])
    width = duration / period
    best = (-np.inf, np.nan, np.nan)

    # Evaluate windows beginning at each observed phase. This is intentionally
    # straightforward and can be optimized later for hardware exploration.
    for start_idx in range(n):
        start_phase = phase_sorted[start_idx]
        end_phase = start_phase + width
        end_idx = np.searchsorted(phase2, end_phase, side="left")
        count_in = end_idx - start_idx
        if count_in < 2 or count_in >= n:
            continue
        sum_in = prefix[end_idx] - prefix[start_idx]
        mean_in = sum_in / count_in
        count_out = n - count_in
        sum_total = np.sum(flux_sorted)
        mean_out = (sum_total - sum_in) / count_out
        depth = mean_out - mean_in
        # Simple score: favors coherent, deeper windows; not a statistical
        # significance or probability.
        score = (count_in * count_out / n) * (depth ** 2)
        if score > best[0]:
            best = (score, depth, start_phase * period)
    return best


def run_search(time_days, flux):
    periods = np.linspace(PERIOD_MIN, PERIOD_MAX, NUM_PERIODS)
    rows = []
    best_global = (-np.inf, None, None, None, None)
    for period in periods:
        for duration in DURATIONS:
            score, depth, epoch = score_period_duration(time_days, flux, period, duration)
            rows.append((period, duration, score, depth, epoch))
            if score > best_global[0]:
                best_global = (score, period, duration, depth, epoch)
    return periods, rows, best_global


def main():
    print("=" * 60)
    print("EXOPLANET TRANSIT DETECTION — BLS-STYLE BASELINE")
    print("=" * 60)
    time_days, flux = generate_synthetic_light_curve()
    print(f"Number of observations: {len(time_days)}")
    print(f"Observation span: {time_days[-1] - time_days[0]:.2f} days")
    print(f"Trial periods: {NUM_PERIODS}")
    print(f"Trial durations: {len(DURATIONS)}")
    print("Running period search...")
    start = time.perf_counter()
    periods, rows, best = run_search(time_days, flux)
    runtime = time.perf_counter() - start

    score, detected_period, detected_duration, estimated_depth, estimated_epoch = best
    period_error = abs(detected_period - TRUE_PERIOD)
    relative_error = 100.0 * period_error / TRUE_PERIOD

    print("\nKNOWN INJECTED SIGNAL")
    print(f"True period:        {TRUE_PERIOD:.5f} days")
    print(f"True duration:      {TRUE_DURATION:.5f} days")
    print(f"True transit depth: {TRUE_DEPTH:.5f}")
    print("\nBEST DETECTED CANDIDATE")
    print(f"Detected period:    {detected_period:.5f} days")
    print(f"Detected duration:  {detected_duration:.5f} days")
    print(f"Estimated depth:    {estimated_depth:.5f}")
    print(f"Detection score:    {score:.5f}")
    print(f"Period error:       {period_error:.5f} days ({relative_error:.3f}%)")
    print(f"Search runtime:     {runtime:.4f} seconds")

    np.savetxt(OUTPUT_DIR / "synthetic_light_curve.csv",
               np.column_stack([time_days, flux]), delimiter=",",
               header="time_days,normalized_flux", comments="")
    search_array = np.array(rows, dtype=float)
    np.savetxt(OUTPUT_DIR / "bls_search_results.csv", search_array, delimiter=",",
               header="trial_period_days,duration_days,score,estimated_depth,epoch_days", comments="")
    metrics = [
        ("n_observations", len(time_days)),
        ("observation_span_days", time_days[-1] - time_days[0]),
        ("trial_periods", NUM_PERIODS),
        ("trial_durations", len(DURATIONS)),
        ("true_period_days", TRUE_PERIOD),
        ("detected_period_days", detected_period),
        ("absolute_period_error_days", period_error),
        ("relative_period_error_percent", relative_error),
        ("true_duration_days", TRUE_DURATION),
        ("detected_duration_days", detected_duration),
        ("true_depth", TRUE_DEPTH),
        ("estimated_depth", estimated_depth),
        ("detection_score", score),
        ("runtime_seconds", runtime),
    ]
    with (OUTPUT_DIR / "baseline_metrics.csv").open("w", encoding="utf-8") as f:
        f.write("metric,value\n")
        for name, value in metrics:
            f.write(f"{name},{value}\n")

    if plt is not None:
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.scatter(time_days, flux, s=5)
        ax.set_title("Synthetic light curve with injected transit")
        ax.set_xlabel("Time (days)")
        ax.set_ylabel("Normalized flux")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "light_curve.png", dpi=160)
        plt.close(fig)

        # For each trial period, retain the highest score across durations.
        best_by_period = []
        for p in periods:
            scores = [r[2] for r in rows if np.isclose(r[0], p)]
            best_by_period.append(max(scores))
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(periods, best_by_period)
        ax.axvline(TRUE_PERIOD, linestyle="--", label="Injected period")
        ax.set_title("BLS-style period search")
        ax.set_xlabel("Trial period (days)")
        ax.set_ylabel("Best transit-window score")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "periodogram.png", dpi=160)
        plt.close(fig)
        print(f"\nPlots saved in: {OUTPUT_DIR.resolve()}")
    else:
        print("\nMatplotlib not installed; skipped plot generation.")
    print(f"CSV results saved in: {OUTPUT_DIR.resolve()}")
    print("\nNOTE: This simplified educational baseline must be validated")
    print("against a trusted BLS implementation before scientific use.")


if __name__ == "__main__":
    main()
