# Exoplanet Transit Detection: Python Baseline

A learning and research project exploring **exoplanet transit detection** using a simplified Box Least Squares (BLS)-style search, with a longer-term goal of investigating FPGA acceleration and ASIC-oriented design-space exploration.

> **Current status:** The current results use **synthetic data only**. Real Kepler/TESS light-curve validation is planned and has not yet been completed.

## Why this project?

When a planet passes in front of its host star, the measured brightness can drop slightly. This is called a *transit*. Transit-search algorithms look for repeated, transit-shaped dips in stellar brightness measurements (a light curve).

This project starts with a controlled synthetic signal so that the injected orbital period and transit depth are known. That makes it possible to check whether the baseline search can recover a known signal before moving to real telescope data and hardware implementation.

## Current synthetic experiment

The initial experiment used 1,350 simulated observations over 27 days. A periodic transit signal was injected into the light curve with Gaussian noise.

| Parameter | Value |
|---|---:|
| Number of observations | 1,350 |
| Observation span | 27 days |
| Trial periods | 400 |
| Trial durations | 5 |
| Injected orbital period | 3.70000 days |
| Detected period | 3.69424 days |
| Absolute period error | 0.00576 days |
| Relative period error | ~0.156% |
| Injected transit depth | 1.000% |
| Estimated transit depth | 0.922% |
| Detected duration | 0.12000 days |
| Search runtime in the original environment | ~7.03 seconds |

These are preliminary results from a **simplified BLS-style educational baseline**. Runtime depends on the execution environment and should not be treated as a hardware performance measurement. The detection score is an implementation-specific score, not a probability that a planet exists.

## Figures

The figures below show the synthetic light curve and the period-search score. They illustrate the current experiment, not observations from a real telescope.

- `results/light_curve.png`
- `results/periodogram.png`

## Run the code

The baseline is designed to run with NumPy. Matplotlib is optional for generating plots.

```bash
python -m venv .venv
```

Activate the environment:

**Windows (Command Prompt):**
```bat
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python exoplanet_bls_baseline.py
```

The script writes generated CSV files and plots to `results/`.

## Repository structure

```text
exoplanet-transit-detection/
├── README.md
├── exoplanet_bls_baseline.py
├── requirements.txt
├── .gitignore
├── LICENSE
├── data/
│   └── README.md
└── results/
    ├── baseline_metrics.csv
    ├── light_curve.png
    └── periodogram.png
```

## Roadmap

- [x] Generate a synthetic stellar light curve with a known transit.
- [x] Implement an initial BLS-style period search.
- [x] Recover a period close to the injected period in the initial experiment.
- [ ] Validate against a trusted BLS implementation (for example, Astropy's BLS).
- [ ] Test recovery over multiple noise levels and transit depths.
- [ ] Analyze real Kepler light curves from NASA's MAST archive.
- [ ] Compare detections with published planet parameters in the NASA Exoplanet Archive.
- [ ] Test generalization on TESS light curves.
- [ ] Profile the computational bottlenecks and define a hardware-friendly algorithm.
- [ ] Prototype the selected architecture on FPGA.
- [ ] Explore ASIC-oriented synthesis and design-space trade-offs.

## Planned real-data sources

- **MAST archive:** https://archive.stsci.edu/
- **NASA Exoplanet Archive:** https://exoplanetarchive.ipac.caltech.edu/
- **Astropy Box Least Squares documentation:** https://docs.astropy.org/en/stable/timeseries/bls.html
- **Lightkurve documentation:** https://lightkurve.github.io/lightkurve/

Real-data analysis is future work. No claim is made here that the current baseline has been validated on Kepler or TESS observations.

## Research direction

The longer-term research question is how numerical precision, parallelism, memory access, and candidate-vetting complexity affect the trade-off between detection performance and hardware efficiency.

Potential evaluation metrics include:

- Period recovery error and transit-depth error
- Detection completeness and false-positive rate across injection-recovery tests
- Runtime, throughput, and latency
- FPGA LUT, FF, DSP, and BRAM utilization
- Timing closure and power estimates
- ASIC standard-cell area, timing, and power estimates (where supported by the design flow)

These metrics will be evaluated as the project develops; they are not all measured in the current experiment.

## Important limitations

1. The current input is synthetic, not real astronomical data.
2. This is a simplified BLS-style implementation, not a claim of a fully validated or production-grade scientific BLS implementation.
3. A single successful recovery does not establish general detection reliability.
4. The reported Python runtime is environment-specific and cannot be compared directly with a future FPGA runtime without a controlled benchmark.
5. The project does not claim novelty until a systematic literature review establishes the relevant research gap.

## Acknowledgements

This project is an independent research and learning effort at the intersection of astronomy, signal processing, and digital hardware design. NASA MAST and the NASA Exoplanet Archive are planned sources for future real-data experiments.
