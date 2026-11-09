#!/bin/bash
# ==============================================================================
# NS-2 Simulation Runner & AWK Analyzer Script
# Project: Smart City Network Simulation and Congestion Analysis
# Usage:
#   chmod +x run_ns2_simulation.sh
#   ./run_ns2_simulation.sh
# ==============================================================================

echo "======================================================================"
echo "    Running Smart City NS-2 Simulations & AWK Metrics Analysis       "
echo "======================================================================"

# Check if ns is installed
if ! command -v ns &> /dev/null; then
    echo "[WARNING] 'ns' (NS-2) was not found in PATH."
    echo "To install NS-2 on Ubuntu/Debian: sudo apt-get update && sudo apt-get install ns2 nam"
    echo "Running trace analysis with python on sample trace files instead..."
    python3 python_simulation/analyze_trace.py results/trace_samples/smart_city_baseline.tr
    python3 python_simulation/analyze_trace.py results/trace_samples/smart_city_leaky_bucket.tr
    exit 0
fi

echo "[1/3] Running Baseline Congestion Simulation..."
ns ns2_scripts/smart_city_baseline.tcl

echo "[2/3] Running Leaky Bucket Traffic Shaping Simulation..."
ns ns2_scripts/smart_city_leaky_bucket.tcl

echo "[3/3] Running TCP vs UDP Congestion Comparison..."
ns ns2_scripts/tcp_vs_udp_comparison.tcl

echo ""
echo "======================================================================"
echo "                   AWK ANALYSIS: BASELINE SCENARIO                    "
echo "======================================================================"
awk -f awk/throughput.awk smart_city_baseline.tr
awk -f awk/packet_drop.awk smart_city_baseline.tr
awk -f awk/pdr.awk smart_city_baseline.tr
awk -f awk/delay.awk smart_city_baseline.tr
awk -f awk/buffer_utilization.awk smart_city_baseline.tr

echo ""
echo "======================================================================"
echo "                 AWK ANALYSIS: LEAKY BUCKET SCENARIO                  "
echo "======================================================================"
awk -f awk/throughput.awk smart_city_leaky_bucket.tr
awk -f awk/packet_drop.awk smart_city_leaky_bucket.tr
awk -f awk/pdr.awk smart_city_leaky_bucket.tr
awk -f awk/delay.awk smart_city_leaky_bucket.tr
awk -f awk/buffer_utilization.awk smart_city_leaky_bucket.tr

echo ""
echo "======================================================================"
echo " NS-2 Simulations and AWK analysis completed successfully!"
echo " To view Network Animator (NAM), run: "
echo "   nam smart_city_baseline.nam &"
echo "   nam smart_city_leaky_bucket.nam &"
echo "   nam tcp_vs_udp_comparison.nam &"
echo "======================================================================"
