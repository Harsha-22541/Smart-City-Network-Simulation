# Smart City Network Simulation and Congestion Analysis

A comprehensive simulation framework to model, analyze, and mitigate network congestion in a Smart City IoT infrastructure. Built for **NS-2 (Network Simulator 2)** with cross-platform native **Python Discrete-Event Simulation & Visualization**.

---

## 🌆 Problem Overview

A modern Smart City relies on interconnected cyber-physical systems:
- **Traffic Signals & Actuators**: Periodic vehicle flow telemetry.
- **CCTV Surveillance Cameras**: High-definition, high-bandwidth bursty video streams.
- **Pollution & Environmental Sensors**: Periodic telemetry reporting air quality.
- **Smart Street Lighting**: Low-latency illumination telemetry and control.
- **Central Traffic Management Center (TMC)**: Centralized coordination cloud server.
- **Emergency Services**: High-priority alert traffic from ambulances, police, and fire rescue.

When dozens of devices transmit simultaneously across shared aggregation links, severe buffer overflow, queuing delays, and packet loss occur at the central gateway router. This project models this congestion behavior, applies the **Leaky Bucket Algorithm** for traffic shaping and buffer management, and compares **TCP vs UDP** transport dynamics under congestion.

---

## 📁 Project Structure

```
c:\Users\hv728\OneDrive\Desktop\CNIP\
│
├── ns2_scripts/                           # NS-2 Simulation Scripts (OTcl)
│   ├── smart_city_main.tcl                # Master script with configurable shaping & buffer
│   ├── smart_city_baseline.tcl            # Uncontrolled congestion scenario (DropTail)
│   ├── smart_city_leaky_bucket.tcl        # Leaky Bucket shaped scenario
│   └── tcp_vs_udp_comparison.tcl          # TCP (AIMD) vs UDP (CBR) competition & CWND trace
│
├── awk/                                   # Trace Analysis Scripts (NS-2 Trace format)
│   ├── throughput.awk                     # Periodic & average throughput calculation
│   ├── packet_drop.awk                    # Packet drop analysis by flow and router
│   ├── pdr.awk                            # Packet Delivery Ratio (PDR %)
│   ├── delay.awk                          # End-to-end packet transmission latency
│   └── buffer_utilization.awk             # Bottleneck buffer occupancy & queue length
│
├── src_leaky_bucket/                      # Core Leaky Bucket Implementations
│   ├── leaky_bucket.py                    # Python implementation with trace table
│   ├── leaky_bucket.c                     # Standard C implementation
│   └── leaky_bucket.cpp                   # Object-oriented C++ implementation
│
├── python_simulation/                     # Discrete-Event Simulation & Plotting (Windows/Linux)
│   ├── simulate_smart_city.py             # Full Smart City discrete event simulation engine
│   ├── plot_results.py                    # Generates 5 publication-quality graphs
│   └── analyze_trace.py                   # Python equivalent of the AWK trace analyzer
│
├── results/
│   ├── graphs/                            # High-resolution simulation plots (PNG)
│   │   ├── 1_throughput_comparison.png
│   │   ├── 2_packet_drop_analysis.png
│   │   ├── 3_buffer_utilization.png
│   │   ├── 4_tcp_vs_udp_congestion.png
│   │   └── 5_network_topology.png
│   └── trace_samples/                     # Generated NS-2 trace files (.tr)
│       ├── smart_city_baseline.tr
│       └── smart_city_leaky_bucket.tr
│
├── run_analysis.py                        # Master Python execution runner
├── run_all.bat                            # 1-Click Windows execution script
├── run_ns2_simulation.sh                  # 1-Click Linux/WSL/Ubuntu NS-2 script
├── README.md                              # Project documentation
└── PROJECT_REPORT.md                      # Academic report with equations & results
```

---

## 🚀 How to Run

### Option 1: Native Windows Execution (Python Engine & Graph Generator)

No Linux or NS-2 installation required. Runs directly in Windows PowerShell or Command Prompt:

```powershell
# Run the complete analysis pipeline (Leaky Bucket, simulation, trace analyzer, and graphs)
python run_analysis.py
```
Or double-click `run_all.bat`.

### Option 2: Linux / Ubuntu / WSL (Native NS-2 Environment)

1. Make the shell script executable and run:
```bash
chmod +x run_ns2_simulation.sh
./run_ns2_simulation.sh
```

2. Run individual NS-2 simulations:
```bash
# Baseline uncontrolled congestion
ns ns2_scripts/smart_city_baseline.tcl

# Leaky Bucket traffic shaping
ns ns2_scripts/smart_city_leaky_bucket.tcl

# TCP vs UDP congestion comparison
ns ns2_scripts/tcp_vs_udp_comparison.tcl
```

3. Analyze the generated `.tr` trace files using AWK:
```bash
awk -f awk/throughput.awk smart_city_baseline.tr
awk -f awk/packet_drop.awk smart_city_baseline.tr
awk -f awk/pdr.awk smart_city_baseline.tr
awk -f awk/delay.awk smart_city_baseline.tr
awk -f awk/buffer_utilization.awk smart_city_baseline.tr
```

4. Visualize in Network Animator (NAM):
```bash
nam smart_city_baseline.nam &
nam smart_city_leaky_bucket.nam &
nam tcp_vs_udp_comparison.nam &
```

---

## 📊 Key Results Summary

| Performance Metric | Baseline (Uncontrolled DropTail) | Leaky Bucket Shaped Traffic | Improvement / Impact |
| :--- | :---: | :---: | :---: |
| **Total Injected Packets** | 7,754 | 5,449 | Regulated input load |
| **Delivered Packets** | 2,554 | 4,543 | **+77.8% higher delivery** |
| **Dropped Packets** | 5,200 | 906 | **82.6% drop reduction** |
| **Packet Delivery Ratio (PDR)** | **32.94%** | **83.37%** | **+50.43% improvement** |
| **Average Goodput Throughput** | 1.462 Mbps | 2.613 Mbps | **+78.7% throughput** |
| **Emergency Services Delivery** | 0% (Starved by CCTV) | **100% (Guaranteed)** | **Zero packet loss** |
| **Pollution & Light Sensors** | 17% delivery (high loss) | **100% (Guaranteed)** | **Zero packet loss** |
| **Peak Gateway Queue** | 15 pkts (overflowing) | Regulated buffer (Smooth) | Controlled queueing |

---

## 📈 Visualizations Generated

All graphs are located in `results/graphs/`:
1. `1_throughput_comparison.png`: Instantaneous and cumulative throughput (Baseline vs Leaky Bucket).
2. `2_packet_drop_analysis.png`: Packet drops across device types and sensitivity vs buffer size.
3. `3_buffer_utilization.png`: Gateway buffer occupancy vs time showing overflow spikes vs smoothed regulated queue.
4. `4_tcp_vs_udp_congestion.png`: TCP Congestion Window (AIMD) evolution and TCP vs UDP bandwidth competition.
5. `5_network_topology.png`: Network topology diagram detailing nodes, edge links, and bottleneck links.
