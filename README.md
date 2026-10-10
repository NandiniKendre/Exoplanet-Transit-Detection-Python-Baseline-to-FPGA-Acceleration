# Exoplanet Transit Detection Using Verilog and FPGA

A Verilog RTL-based research project for **exoplanet transit detection using a simplified Box Least Squares (BLS)-style search**. The project combines a Python reference baseline with a synthesizable digital hardware architecture, RTL simulation in Xilinx Vivado, and future FPGA prototyping and ASIC-oriented design-space exploration.

> **Current status:** Synthetic-data experiments and Verilog RTL simulation. Real Kepler/TESS validation, on-board FPGA testing, and ASIC implementation remain future work unless explicitly documented in subsequent results.

## Project Overview

An exoplanet can be detected when it passes in front of its host star, causing a small, periodic decrease in measured stellar brightness. A light curve records these brightness measurements over time.

The Box Least Squares (BLS) method searches for periodic, approximately box-shaped dips in a light curve by evaluating candidate orbital periods and transit durations.

This project investigates how the computationally intensive parts of transit detection can be mapped to digital hardware using **Verilog HDL**, with emphasis on deterministic processing, parallel computation, fixed-point arithmetic, memory organization, and hardware resource efficiency.

The long-term objective is to develop an FPGA-accelerated transit-search architecture and investigate its potential for ASIC implementation.

## Project Objectives

- Develop a Python reference implementation for synthetic transit generation and period searching.
- Design a Verilog RTL architecture for hardware-oriented transit detection.
- Verify RTL functionality using testbenches and waveform analysis in Xilinx Vivado.
- Compare hardware outputs against known synthetic signal parameters and software reference results.
- Investigate fixed-point precision, parallelism, throughput, latency, and resource utilization.
- Progress toward FPGA implementation, followed by ASIC-oriented synthesis and design-space exploration.

## System Architecture

The intended development flow is:

```text
Synthetic Light-Curve Generation
              |
              v
     Python BLS Reference
              |
              v
     Verilog RTL Design
              |
              v
     Vivado RTL Simulation
              |
              v
  Functional and Numerical Checks
              |
              v
    FPGA Synthesis and Timing
              |
              v
     FPGA Hardware Validation
              |
              v
  ASIC-Oriented Design Exploration
```

The Python implementation provides a reference for the algorithm. The Verilog implementation explores how the selected computations can be organized into clocked hardware.

The precise division of computation between software and RTL will depend on the current hardware implementation. The complete BLS search should not be considered implemented in hardware unless all required search stages are present in the RTL.

## 1. Python Reference Baseline

The initial experiment uses a synthetic light curve with a known periodic transit signal and Gaussian noise.

| Parameter | Value |
|---|---:|
| Number of observations | 1,350 |
| Observation span | 27 days |
| Trial periods | 400 |
| Trial durations | 5 |
| Injected orbital period | 3.70000 days |
| Detected period | 3.69424 days |
| Absolute period error | 0.00576 days |
| Relative period error | Approximately 0.156% |
| Injected transit depth | 1.000% |
| Estimated transit depth | 0.922% |
| Detected duration | 0.12000 days |
| Original Python search runtime | Approximately 7.03 seconds |

These results are preliminary and come from one synthetic-data experiment. The runtime is environment-specific and is not a hardware speedup benchmark.

The detection score is implementation-specific and should not be interpreted as the probability that an exoplanet exists.

## 2. Verilog RTL Implementation

The hardware-design stage translates selected transit-detection computations into a clock-driven RTL architecture.

**Target development environment:** Xilinx Vivado  
**Hardware description language:** Verilog HDL  
**Verification method:** RTL testbench simulation with waveform and numerical-result inspection

The current RTL experiment uses the following synthetic test configuration:

| Parameter | RTL simulation configuration |
|---|---:|
| Clock frequency | 100 MHz |
| Clock period | 10 ns |
| Number of light-curve samples | 1,350 |
| Injected orbital period | 3.70 days |
| Injected transit duration | 0.12 days |
| Injected transit depth | 1% |
| Input data | Synthetic |

The simulation stimulus injects a known transit signal and evaluates the RTL processing sequence. These input parameters describe the test scenario; they do not independently establish that every parameter is recovered accurately by the hardware.

### RTL verification goals

- Verify reset behavior and initialization.
- Confirm correct input-sample sequencing.
- Validate the controller and processing state transitions.
- Check arithmetic operations and intermediate values.
- Verify candidate-period or transit-score calculations implemented in RTL.
- Compare RTL outputs against a software reference or independently calculated expected values.
- Measure clock cycles and simulation latency for the implemented hardware operations.

**Important:** The complete BLS search is only considered hardware-implemented when period evaluation, duration evaluation, score calculation, and best-candidate selection are implemented and verified in RTL. Any stages not yet implemented will remain part of the roadmap.

## 3. Vivado Simulation and Hardware Metrics

Vivado RTL simulation establishes functional behavior but does not, by itself, establish FPGA hardware performance.

The following metrics will be recorded as the implementation progresses:

| Metric | Evaluation method |
|---|---|
| Functional correctness | Testbench and reference-output comparison |
| Period recovery error | Compare detected and injected periods |
| Transit-depth error | Compare estimated and injected depths |
| Clock cycles per search | RTL simulation or cycle-count analysis |
| Processing latency | Clock cycles × clock period |
| Throughput | Valid outputs processed per unit time |
| LUT and FF utilization | FPGA synthesis reports |
| BRAM and DSP utilization | FPGA synthesis reports |
| Maximum operating frequency | Timing analysis |
| Power estimate | Vivado power analysis, when supported |

No FPGA speedup, resource utilization, timing closure, or power result is claimed here without the corresponding implementation report.

### Latency calculation

For a 100 MHz clock:

\[
T_{\mathrm{clk}}=\frac{1}{100\,\mathrm{MHz}}=10\,\mathrm{ns}
\]

If a measured operation takes \(N\) clock cycles, its nominal cycle-based latency is:

\[
T_{\mathrm{latency}}=N \times 10\,\mathrm{ns}
\]

This calculation describes the specified clock-cycle count. Actual board-level performance requires synthesis, timing analysis, and hardware validation.

## 4. Repository Structure

```text
exoplanet-transit-detection/
├── README.md
├── python/
│   ├── exoplanet_bls_baseline.py
│   └── requirements.txt
├── rtl/
│   ├── README.md
│   ├── top_module.v
│   └── [additional RTL modules]
├── testbench/
│   ├── tb_exoplanet_detection.v
│   └── [additional testbenches]
├── data/
│   └── README.md
├── results/
│   ├── baseline_metrics.csv
│   ├── light_curve.png
│   ├── periodogram.png
│   └── [RTL simulation reports]
└── docs/
    └── architecture.md
```

*The tree above is a suggested structure. Keep only files and directories that actually exist in the repository, and replace example RTL filenames with the names used by your design.*

## 5. Running the Python Baseline

Create and activate a virtual environment.

**Windows:**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the required packages and execute the baseline:

```bash
python -m pip install -r python/requirements.txt
python python/exoplanet_bls_baseline.py
```

The exact commands depend on the actual location of the script and dependency file in the repository. Generated figures and CSV results should be saved in the configured results directory.

## 6. Running the Verilog Simulation

1. Open Xilinx Vivado.
2. Create or open the RTL project.
3. Add the Verilog source files from `rtl/`.
4. Add the testbench files from `testbench/`.
5. Configure the testbench as the simulation top module.
6. Run **Run Behavioral Simulation**.
7. Inspect the waveform, reset sequence, state transitions, counters, and output signals.
8. Compare the simulated outputs against expected values.
9. Record the simulation configuration and measured results.

For reproducible experiments, save the testbench, simulation logs, waveform captures, and expected-versus-actual result comparisons in the repository.

## 7. Research Roadmap

### Phase 1 — Software validation

- [x] Generate a synthetic stellar light curve.
- [x] Implement an initial simplified BLS-style search.
- [x] Recover a period close to the injected period in the initial experiment.
- [ ] Compare against Astropy's trusted BLS implementation.
- [ ] Evaluate recovery across multiple noise levels and transit depths.

### Phase 2 — Verilog RTL development

- [x] Establish a synthetic RTL simulation scenario.
- [x] Run the initial Vivado RTL simulation.
- [ ] Document the verified RTL module hierarchy.
- [ ] Verify reset, control logic, arithmetic, and candidate selection.
- [ ] Compare RTL results against an independent reference.
- [ ] Evaluate numerical precision and fixed-point arithmetic.
- [ ] Measure cycle counts and end-to-end RTL latency.
- [ ] Test edge cases and parameter variations.

### Phase 3 — FPGA implementation

- [ ] Synthesize the verified RTL design.
- [ ] Evaluate LUT, FF, BRAM, and DSP utilization.
- [ ] Perform timing analysis and assess maximum operating frequency.
- [ ] Optimize the datapath and memory architecture.
- [ ] Implement the design on a selected FPGA board.
- [ ] Validate results using reproducible test vectors.
- [ ] Compare software and FPGA implementations under controlled conditions.

### Phase 4 — Real astronomical data

- [ ] Obtain Kepler light curves from NASA's MAST archive.
- [ ] Compare candidate detections against published exoplanet parameters.
- [ ] Test the workflow on TESS observations.
- [ ] Evaluate detection completeness, false positives, and robustness.
- [ ] Assess the effect of stellar variability, missing samples, and measurement noise.

### Phase 5 — ASIC-oriented design-space exploration

- [ ] Define a synthesizable hardware architecture suitable for ASIC evaluation.
- [ ] Compare resource and timing trade-offs across numerical precisions.
- [ ] Investigate parallel versus resource-shared architectures.
- [ ] Explore memory organization and datapath pipelining.
- [ ] Run standard-cell synthesis using an available technology library.
- [ ] Evaluate area, timing, and power estimates.
- [ ] Perform physical-design evaluation where the required tools and libraries are available.

## 8. Planned Data and Reference Resources

- **NASA MAST:** https://archive.stsci.edu/
- **NASA Exoplanet Archive:** https://exoplanetarchive.ipac.caltech.edu/
- **Astropy Box Least Squares:** https://docs.astropy.org/en/stable/timeseries/bls.html
- **Lightkurve:** https://lightkurve.github.io/lightkurve/
- **Xilinx Vivado Design Suite:** https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html

Real-data validation and FPGA board testing are planned activities, not established outcomes of the initial synthetic experiment.

## 9. Research Questions

The project will investigate the following questions:

1. How accurately can a hardware-oriented transit-search implementation recover an injected orbital period and transit depth?
2. How does fixed-point precision affect detection accuracy and hardware cost?
3. What is the trade-off between parallel period evaluation and resource sharing?
4. How do pipelining, memory access, and candidate-selection logic affect latency and throughput?
5. How do FPGA resource requirements change with the number of observations, trial periods, and trial durations?
6. Which architecture offers a practical starting point for ASIC implementation?
7. How does performance on synthetic data compare with performance on real astronomical light curves?

## 10. Limitations and Scope

- The current experiment uses synthetic data.
- The Python implementation is a simplified BLS-style educational baseline and has not yet been independently validated against Astropy BLS.
- The initial period recovery result does not establish general detection reliability.
- RTL simulation is not equivalent to FPGA board validation.
- Python runtime cannot be compared directly with FPGA latency without a controlled benchmark using equivalent workloads.
- Hardware metrics must be supported by synthesis, timing, and power reports.
- ASIC feasibility and research novelty require further investigation and supporting evidence.

## Acknowledgements

This project is an independent learning and research effort at the intersection of astronomy, signal processing, Verilog RTL design, and digital hardware acceleration.

NASA MAST, the NASA Exoplanet Archive, Astropy, and Lightkurve are planned resources for future scientific validation.

---

**Project focus:** Verilog RTL implementation → Vivado verification → FPGA acceleration → ASIC-oriented design-space exploration.
