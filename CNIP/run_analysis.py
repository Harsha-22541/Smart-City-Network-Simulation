"""
==============================================================================
Master Execution & Analysis Runner
Project: Smart City Network Simulation and Congestion Analysis
Description:
    One-click runner that executes:
    1. Standalone Leaky Bucket algorithm tests
    2. Full Smart City network simulation (Baseline vs Leaky Bucket vs TCP/UDP)
    3. Automated NS-2 trace file generation and analysis
    4. Publication-quality graph generation
==============================================================================
"""

import os
import sys
import subprocess

def print_banner(title):
    print("\n" + "=" * 76)
    print(f" {title.center(74)} ")
    print("=" * 76)

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    python_sim_dir = os.path.join(root_dir, "python_simulation")
    src_lb_dir = os.path.join(root_dir, "src_leaky_bucket")
    graphs_dir = os.path.join(root_dir, "results", "graphs")
    trace_dir = os.path.join(root_dir, "results", "trace_samples")

    print_banner("SMART CITY NETWORK SIMULATION & CONGESTION ANALYSIS")
    print(f" Working Directory : {root_dir}")
    print(f" Simulation Engine : Python 3 & NS-2 (Network Simulator 2)")
    print(f" Target Graphs Dir : {graphs_dir}")

    # 1. Run Leaky Bucket Algorithm
    print_banner("STEP 1: TESTING LEAKY BUCKET ALGORITHM")
    subprocess.run([sys.executable, os.path.join(src_lb_dir, "leaky_bucket.py")], check=True)

    # 2. Run Network Simulation and Plotting
    print_banner("STEP 2: RUNNING NETWORK SIMULATION & GENERATING PLOTS")
    subprocess.run([sys.executable, os.path.join(python_sim_dir, "plot_results.py")], check=True)

    # 3. Analyze Baseline Trace
    print_banner("STEP 3: ANALYZING BASELINE TRACE (UNCONTROLLED CONGESTION)")
    baseline_tr = os.path.join(trace_dir, "smart_city_baseline.tr")
    subprocess.run([sys.executable, os.path.join(python_sim_dir, "analyze_trace.py"), baseline_tr], check=True)

    # 4. Analyze Leaky Bucket Trace
    print_banner("STEP 4: ANALYZING LEAKY BUCKET TRACE (SHAPED CONGESTION AVOIDANCE)")
    lb_tr = os.path.join(trace_dir, "smart_city_leaky_bucket.tr")
    subprocess.run([sys.executable, os.path.join(python_sim_dir, "analyze_trace.py"), lb_tr], check=True)

    print_banner("SIMULATION EXECUTION COMPLETED SUCCESSFULLY!")
    print(" Generated Artifacts:")
    print(f"  * Graphs          : {graphs_dir}")
    print(f"  * Trace Samples   : {trace_dir}")
    print(f"  * NS-2 Scripts    : {os.path.join(root_dir, 'ns2_scripts')}")
    print(f"  * AWK Analyzers   : {os.path.join(root_dir, 'awk')}")
    print("=" * 76 + "\n")

if __name__ == "__main__":
    main()
