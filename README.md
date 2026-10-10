# 🌌 Exoplanet Transit Detection Using Verilog and FPGA

🔭 A hardware-oriented research project exploring **exoplanet transit detection using a simplified Box Least Squares (BLS)-style search**. The project combines Python-based algorithm development, Verilog RTL design, Xilinx Vivado simulation, and future FPGA acceleration and ASIC design-space exploration.

> ⚠️ **Current Status:** Initial synthetic-data experiments and Verilog RTL simulation. Validation using real Kepler/TESS light curves, FPGA board testing, and ASIC implementation are planned future stages.

## 🪐 Project Overview

When an exoplanet passes in front of its host star, it causes a small, periodic decrease in the observed stellar brightness. This phenomenon is known as a **transit**.

📈 A light curve records stellar brightness over time, and the Box Least Squares (BLS) method searches for periodic, transit-shaped dips to identify potential exoplanet candidates.

This project explores how transit-detection computations can be implemented using **Verilog HDL** and mapped to digital hardware.

The long-term goal is to develop an FPGA-accelerated transit-search architecture and investigate its suitability for ASIC implementation.

## 🎯 Project Objectives

- 🐍 Develop a Python reference implementation for synthetic transit generation and period searching.
- 💻 Design a Verilog RTL architecture for hardware-oriented transit detection.
- 🧪 Verify RTL functionality through testbenches and waveform analysis in Xilinx Vivado.
- 🔍 Compare RTL outputs against known synthetic parameters and software reference results.
- ⚡ Investigate fixed-point arithmetic, parallelism, latency, and throughput.
- 📊 Evaluate FPGA resource utilization, timing, and power estimates.
- 🏭 Explore ASIC-oriented synthesis and hardware design-space trade-offs.

## 🏗️ System Architecture

```text
🌟 Synthetic Light-Curve Generation
                 |
                 v
🐍 Python BLS Reference Model
                 |
                 v
💻 Verilog RTL Architecture
                 |
                 v
🧪 Vivado RTL Simulation
                 |
                 v
🔍 Functional Verification
                 |
                 v
⚡ FPGA Synthesis & Timing Analysis
                 |
                 v
🔬 FPGA Hardware Validation
                 |
                 v
🏭 ASIC Design-Space Exploration
```

*Note: This is the planned development flow. Each stage will be marked complete after its implementation and verification.*

## 🐍 1. Python Reference Baseline

The initial experiment uses a synthetic stellar light curve with a known periodic transit signal and Gaussian noise.

| Parameter | Result |
|---|---:|
| 📊 Number of observations | 1,350 |
| 🗓️ Observation span | 27 days |
| 🔎 Trial periods | 400 |
| ⏱️ Trial durations | 5 |
| 🪐 Injected orbital period | 3.70000 days |
| 🎯 Detected period | 3.69424 days |
| 📉 Absolute period error | 0.00576 days |
| 📐 Relative period error | ~0.156% |
| 🌑 Injected transit depth | 1.000% |
| 📊 Estimated transit depth | 0.922% |
| ⏳ Detected duration | 0.12000 days |
| 🖥️ Python search runtime | ~7.03 seconds |

✅ The initial synthetic experiment recovered a period close to the injected value.

⚠️ These are preliminary results from a simplified BLS-style implementation. The runtime depends on the execution environment, and the result does not establish general detection reliability.

## 💻 2. Verilog RTL Implementation

The hardware-design stage focuses on translating selected transit-detection computations into clock-driven digital logic.

| Configuration | Value |
|---|---:|
| 🛠️ HDL | Verilog |
| 🧰 Development environment | Xilinx Vivado |
| ⏰ Simulation clock | 100 MHz |
| 🕒 Clock period | 10 ns |
| 📊 Light-curve samples | 1,350 |
| 🪐 Injected orbital period | 3.70 days |
| 🌑 Injected transit depth | 1% |
| ⏱️ Injected transit duration | 0.12 days |
| 🧪 Test data | Synthetic |

### 🔬 RTL Verification Goals

- ✅ Verify reset and initialization behavior.
- 🔄 Validate control logic and state transitions.
- ➗ Check arithmetic operations and intermediate results.
- 📥 Verify input-sample sequencing.
- 🎯 Validate candidate-period and transit-score calculations implemented in RTL.
- 📊 Compare simulated results against expected values.
- ⏱️ Measure clock cycles and processing latency.

**Important:** A complete hardware BLS implementation requires verified RTL for the relevant search stages, including period evaluation, duration evaluation, score calculation, and best-candidate selection. Any stages not yet implemented remain future work.

## 🧪 3. Vivado Simulation and Performance Evaluation

Vivado RTL simulation is used to verify the functional behavior of the hardware design.

Planned evaluation metrics include:

| Metric | Evaluation |
|---|---|
| ✅ Functional correctness | Testbench and reference comparison |
| 🎯 Period recovery | Detected versus injected period |
| 🌑 Transit-depth accuracy | Estimated versus injected depth |
| 🔄 Cycle count | Clock cycles per operation or search |
| ⏱️ Latency | Clock cycles × clock period |
| 🚀 Throughput | Valid results per unit time |
| 🧩 FPGA resources | LUT, FF, BRAM, and DSP utilization |
| ⚡ Timing | Timing analysis and maximum frequency |
| 🔋 Power | Vivado power estimation, where supported |

### ⏰ Clock and Latency Calculation

For a 100 MHz clock:

\[
T_{\mathrm{clk}}=\frac{1}{100\,\mathrm{MHz}}=10\,\mathrm{ns}
\]

If an operation takes \(N\) clock cycles:

\[
T_{\mathrm{latency}}=N \times 10\,\mathrm{ns}
\]

📌 This is a cycle-based calculation. Actual FPGA performance must be established through synthesis, timing analysis, and hardware testing.

## 📁 4. Repository Structure

```text
verilog-exoplanet-transit-detection/
├── 📄 README.md
├── 🐍 python/
│   ├── exoplanet_bls_baseline.py
│   └── requirements.txt
├── 💻 rtl/
│   ├── README.md
│   └── [Verilog RTL modules]
├── 🧪 testbench/
│   └── [Verilog testbenches]
├── 📂 data/
│   └── README.md
├── 📊 results/
│   ├── baseline_metrics.csv
│   ├── light_curve.png
│   ├── periodogram.png
│   └── [RTL simulation results]
└── 📚 docs/
    └── architecture.md
```

📝 This is a suggested structure. Update the tree to match the files actually present in your repository.

## ▶️ 5. Running the Python Baseline

Create a virtual environment.

**🪟 Windows:**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**🐧 Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies and run:

```bash
python -m pip install -r python/requirements.txt
python python/exoplanet_bls_baseline.py
```

📈 Generated figures and CSV files will be saved in the configured results directory.

## 🧰 6. Running the Verilog Simulation in Vivado

1. 🛠️ Open or create a project in Xilinx Vivado.
2. 📂 Add the Verilog source files.
3. 🧪 Add the testbench files.
4. 🎯 Set the testbench as the simulation top module.
5. ▶️ Run **Run Behavioral Simulation**.
6. 📉 Inspect waveforms, state transitions, counters, and output signals.
7. 🔍 Compare actual outputs against expected results.
8. 💾 Save simulation logs, waveform captures, and verification results.

## 🗺️ 7. Research Roadmap

### 🐍 Phase 1: Software Baseline

- [x] Generate a synthetic stellar light curve.
- [x] Implement an initial BLS-style search.
- [x] Recover a period close to the injected value.
- [ ] Validate against Astropy BLS.
- [ ] Evaluate multiple noise levels and transit depths.

### 💻 Phase 2: Verilog RTL Development

- [x] Establish a synthetic RTL simulation scenario.
- [x] Run the initial Vivado RTL simulation.
- [ ] Document the RTL module hierarchy.
- [ ] Verify arithmetic and control logic.
- [ ] Compare RTL outputs against the software reference.
- [ ] Evaluate fixed-point precision.
- [ ] Measure cycle count and latency.
- [ ] Test edge cases and parameter variations.

### ⚡ Phase 3: FPGA Implementation

- [ ] Synthesize the verified RTL design.
- [ ] Evaluate LUT, FF, BRAM, and DSP utilization.
- [ ] Analyze timing and maximum operating frequency.
- [ ] Optimize datapath and memory organization.
- [ ] Implement the design on an FPGA board.
- [ ] Validate hardware outputs.
- [ ] Perform controlled software-versus-FPGA benchmarking.

### 🔭 Phase 4: Real Astronomical Data

- [ ] Obtain Kepler light curves from NASA MAST.
- [ ] Compare candidate detections with published planet parameters.
- [ ] Extend validation to TESS observations.
- [ ] Evaluate detection completeness and false-positive rates.
- [ ] Investigate missing samples, stellar variability, and measurement noise.

### 🏭 Phase 5: ASIC Design-Space Exploration

- [ ] Develop an ASIC-suitable RTL architecture.
- [ ] Evaluate alternative numerical precisions.
- [ ] Compare parallel and resource-shared architectures.
- [ ] Investigate pipelining and memory-access trade-offs.
- [ ] Perform standard-cell synthesis using an available technology library.
- [ ] Evaluate area, timing, and power estimates.
- [ ] Explore physical design where the required tools and libraries are available.

## 🌐 8. Research Resources

- 🔭 **NASA MAST Archive:** https://archive.stsci.edu/
- 🪐 **NASA Exoplanet Archive:** https://exoplanetarchive.ipac.caltech.edu/
- 📚 **Astropy BLS Documentation:** https://docs.astropy.org/en/stable/timeseries/bls.html
- 📈 **Lightkurve Documentation:** https://lightkurve.github.io/
- 🧰 **AMD Xilinx Vivado:** https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado.html

## 🧠 9. Research Questions

1. 🎯 How accurately can hardware recover injected orbital periods and transit depths?
2. 🔢 How does fixed-point precision affect accuracy and hardware utilization?
3. ⚡ What are the trade-offs between parallel period evaluation and resource sharing?
4. ⏱️ How do pipelining and memory organization affect latency and throughput?
5. 📊 How does resource utilization scale with observations, trial periods, and durations?
6. 🏭 Which architecture offers a practical foundation for ASIC implementation?
7. 🔭 How well do synthetic-data results generalize to real Kepler and TESS observations?

## ⚠️ 10. Limitations

- 🧪 Current experiments use synthetic data.
- 📚 The Python baseline is a simplified BLS-style implementation that still requires independent validation.
- 🎯 A single successful period recovery does not establish general detection reliability.
- 💻 RTL simulation does not prove FPGA board-level performance.
- ⚖️ Python runtime and FPGA latency require controlled benchmarking before comparison.
- 📊 Hardware metrics must be supported by actual synthesis, timing, and power reports.
- 🔍 Research novelty requires a systematic literature review.

## 🙌 Acknowledgements

This independent research and learning project combines **astronomy, signal processing, Verilog RTL design, FPGA acceleration, and ASIC-oriented hardware exploration**.

NASA MAST, the NASA Exoplanet Archive, Astropy, and Lightkurve are planned resources for future scientific validation.

---

### 🚀 Project Focus

**🌌 Astronomy → 💻 Verilog RTL → 🧪 Vivado Verification → ⚡ FPGA Acceleration → 🏭 ASIC Design Exploration**
