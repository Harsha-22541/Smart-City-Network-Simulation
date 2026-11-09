"""
==============================================================================
Smart City Network Simulation: Comprehensive Visualization Module
Project: Smart City Network Simulation and Congestion Analysis
Description:
    Generates high-resolution publication-quality plots analyzing:
    1. Throughput Dynamics (Baseline vs Leaky Bucket)
    2. Packet Drops across Traffic Categories and Buffer Capacities
    3. Gateway Buffer Utilization & Queue Occupancy over Time
    4. TCP vs UDP Congestion Competition & CWND Dynamics
    5. Network Topology Diagram
==============================================================================
"""

import os
import matplotlib
matplotlib.use("Agg") # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

from simulate_smart_city import SmartCitySimulator

# Styling configurations for professional visual presentation
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.sans-serif": "Arial",
    "font.family": "sans-serif",
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14
})

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "graphs")
TRACE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "trace_samples")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TRACE_DIR, exist_ok=True)

def generate_all_plots():
    sim = SmartCitySimulator(sim_duration=10.0, time_step=0.05)
    
    print("Running baseline scenario...")
    res_base = sim.run_scenario(use_leaky_bucket=False, buffer_capacity=15)
    
    print("Running leaky bucket scenario...")
    res_lb = sim.run_scenario(use_leaky_bucket=True, buffer_capacity=30)

    # Save authentic sample NS-2 trace files
    with open(os.path.join(TRACE_DIR, "smart_city_baseline.tr"), "w") as f:
        f.write("\n".join(res_base["trace_records"]))
    with open(os.path.join(TRACE_DIR, "smart_city_leaky_bucket.tr"), "w") as f:
        f.write("\n".join(res_lb["trace_records"]))
    print("Exported NS-2 compatible trace files into results/trace_samples/")

    # -------------------------------------------------------------------------
    # Plot 1: Throughput Comparison (Baseline vs Leaky Bucket)
    # -------------------------------------------------------------------------
    print("Generating Plot 1: Throughput Comparison...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    t = res_base["time_series"]
    ax1.plot(t, res_base["throughput_log"], label="Baseline (DropTail - Uncontrolled)", color="#d9534f", linewidth=1.8)
    ax1.plot(t, res_lb["throughput_log"], label="Leaky Bucket Shaped Traffic", color="#2e6da4", linewidth=2.0)
    ax1.axhline(y=3500, color="black", linestyle="--", alpha=0.7, label="Bottleneck Capacity (3.5 Mbps)")
    ax1.set_ylabel("Instant Throughput (Kbps)")
    ax1.set_title("Network Throughput Dynamics under Bursty Smart City Load", fontweight="bold")
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Cumulative throughput
    cum_base = np.cumsum(res_base["throughput_log"]) * sim.dt / (8 * 1024) # MB
    cum_lb = np.cumsum(res_lb["throughput_log"]) * sim.dt / (8 * 1024)
    ax2.plot(t, cum_base, label="Baseline Delivered Volume", color="#d9534f", linewidth=1.8)
    ax2.plot(t, cum_lb, label="Leaky Bucket Delivered Volume", color="#2e6da4", linewidth=2.0)
    ax2.set_xlabel("Simulation Time (seconds)")
    ax2.set_ylabel("Cumulative Data Delivered (MB)")
    ax2.set_title("Cumulative Data Delivery to Central TMC", fontweight="bold")
    ax2.legend(loc="upper left", frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "1_throughput_comparison.png"), dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Plot 2: Packet Drops by Category & Buffer Size Sensitivity
    # -------------------------------------------------------------------------
    print("Generating Plot 2: Packet Drop Analysis...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

    categories = ["Traffic Signals", "CCTV Video", "Pollution Sensor", "Smart Lighting", "Emergency Service"]
    fids = [1, 2, 3, 4, 5]
    base_drops = [res_base["flow_dropped"].get(f, 0) for f in fids]
    lb_drops = [res_lb["flow_dropped"].get(f, 0) for f in fids]

    x = np.arange(len(categories))
    width = 0.35

    ax1.bar(x - width/2, base_drops, width, label="Baseline (DropTail)", color="#e74c3c", edgecolor="black", alpha=0.85)
    ax1.bar(x + width/2, lb_drops, width, label="Leaky Bucket Shaped", color="#2ecc71", edgecolor="black", alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=25, ha="right")
    ax1.set_ylabel("Total Dropped Packets")
    ax1.set_title("Packet Loss Comparison Across Device Types", fontweight="bold")
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Sensitivity: Packet drop rate vs Buffer Size (5 to 50 packets)
    buffer_sizes = [5, 10, 15, 20, 30, 40, 50]
    base_drop_rates = []
    lb_drop_rates = []
    for b_size in buffer_sizes:
        rb = sim.run_scenario(use_leaky_bucket=False, buffer_capacity=b_size)
        rl = sim.run_scenario(use_leaky_bucket=True, buffer_capacity=b_size)
        base_drop_rates.append(rb["total_dropped"] / rb["total_sent"] * 100.0)
        lb_drop_rates.append(rl["total_dropped"] / rl["total_sent"] * 100.0)

    ax2.plot(buffer_sizes, base_drop_rates, marker="o", color="#e74c3c", linewidth=2.0, label="Baseline (Unregulated)")
    ax2.plot(buffer_sizes, lb_drop_rates, marker="s", color="#2ecc71", linewidth=2.0, label="Leaky Bucket Shaper")
    ax2.set_xlabel("Bottleneck Gateway Buffer Capacity (Packets)")
    ax2.set_ylabel("Packet Drop Rate (%)")
    ax2.set_title("Drop Rate Sensitivity vs Buffer Capacity", fontweight="bold")
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "2_packet_drop_analysis.png"), dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Plot 3: Buffer Occupancy & Utilization Over Time
    # -------------------------------------------------------------------------
    print("Generating Plot 3: Buffer Utilization...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(t, res_base["buffer_occupancy_log"], color="#e67e22", label="Baseline Gateway Queue Length", linewidth=1.8)
    ax1.axhline(y=15, color="red", linestyle="--", linewidth=1.5, label="Queue Limit (15 pkts - Overflow Threshold)")
    ax1.set_ylabel("Queued Packets")
    ax1.set_title("Bottleneck Gateway Buffer Occupancy: Baseline (Severe Overflow)", fontweight="bold")
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    ax2.plot(t, res_lb["buffer_occupancy_log"], color="#27ae60", label="Leaky Bucket Regulated Queue Length", linewidth=1.8)
    ax2.axhline(y=30, color="red", linestyle="--", linewidth=1.5, label="Queue Limit (30 pkts)")
    ax2.set_xlabel("Simulation Time (seconds)")
    ax2.set_ylabel("Queued Packets")
    ax2.set_title("Bottleneck Gateway Buffer Occupancy: Leaky Bucket (Controlled Inflow)", fontweight="bold")
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "3_buffer_utilization.png"), dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Plot 4: TCP vs UDP Congestion Competition
    # -------------------------------------------------------------------------
    print("Generating Plot 4: TCP vs UDP Congestion Comparison...")
    res_tcp_udp = sim.simulate_tcp_vs_udp()
    t_proto = res_tcp_udp["time_series"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Subplot 1: CWND dynamics
    ax1.plot(t_proto, res_tcp_udp["tcp_cwnd"], color="#2980b9", linewidth=2.0, label="TCP Congestion Window (cwnd)")
    ax1.axvspan(2.0, 6.5, color="red", alpha=0.15, label="UDP Bursty Traffic Active Period")
    ax1.set_ylabel("Congestion Window (Packets)")
    ax1.set_title("TCP Congestion Window Dynamics (AIMD Response to Congestion)", fontweight="bold")
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Subplot 2: Throughput sharing
    ax2.plot(t_proto, res_tcp_udp["tcp_throughput"], color="#2980b9", linewidth=2.0, label="TCP Control Throughput")
    ax2.plot(t_proto, res_tcp_udp["udp_throughput"], color="#c0392b", linewidth=2.0, label="UDP Video Feed Throughput")
    ax2.axhline(y=2000, color="black", linestyle="--", alpha=0.7, label="Bottleneck Capacity (2.0 Mbps)")
    ax2.set_xlabel("Simulation Time (seconds)")
    ax2.set_ylabel("Throughput (Kbps)")
    ax2.set_title("Bandwidth Sharing: TCP (Responsive) vs UDP (Aggressive / Unthrottled)", fontweight="bold")
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "4_tcp_vs_udp_congestion.png"), dpi=300)
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Plot 5: Smart City Network Topology
    # -------------------------------------------------------------------------
    print("Generating Plot 5: Network Topology Diagram...")
    draw_network_topology()

    print("All 5 simulation visualization plots generated successfully!")

def draw_network_topology():
    G = nx.Graph()

    # Define nodes with roles and labels
    nodes = {
        0: {"label": "Traffic Signal 1\n(400 Kbps)", "layer": 0, "color": "#3498db", "shape": "s"},
        1: {"label": "Traffic Signal 2\n(400 Kbps)", "layer": 0, "color": "#3498db", "shape": "s"},
        2: {"label": "CCTV Cam 1\n(2.8 Mbps)", "layer": 0, "color": "#e74c3c", "shape": "o"},
        3: {"label": "CCTV Cam 2\n(2.5 Mbps)", "layer": 0, "color": "#e74c3c", "shape": "o"},
        4: {"label": "Pollution Sensor\n(150 Kbps)", "layer": 0, "color": "#2ecc71", "shape": "h"},
        5: {"label": "Smart Lighting\n(120 Kbps)", "layer": 0, "color": "#f39c12", "shape": "h"},
        6: {"label": "Emergency Unit\n(1.5 Mbps)", "layer": 0, "color": "#9b59b6", "shape": "p"},
        7: {"label": "Edge Router 1\n(IoT Aggregator)", "layer": 1, "color": "#34495e", "shape": "D"},
        8: {"label": "Edge Router 2\n(Leaky Bucket Shaper)", "layer": 1, "color": "#16a085", "shape": "D"},
        9: {"label": "Core Gateway\n[Bottleneck 3.5Mb]", "layer": 2, "color": "#d35400", "shape": "D"},
        10: {"label": "Central TMC\nServer & Cloud", "layer": 3, "color": "#2c3e50", "shape": "s"},
    }

    pos = {
        0: (0.0, 5.0),
        1: (0.0, 4.0),
        4: (0.0, 3.0),
        5: (0.0, 2.0),
        2: (0.0, 1.0),
        3: (0.0, 0.0),
        6: (0.0, -1.0),
        7: (2.5, 3.5),
        8: (2.5, 0.0),
        9: (5.0, 1.8),
        10: (7.5, 1.8),
    }

    edges = [
        (0, 7, "5Mb, 2ms"),
        (1, 7, "5Mb, 2ms"),
        (4, 7, "2Mb, 5ms"),
        (5, 7, "2Mb, 5ms"),
        (2, 8, "10Mb, 2ms"),
        (3, 8, "10Mb, 2ms"),
        (6, 8, "10Mb, 1ms"),
        (7, 9, "8Mb, 5ms"),
        (8, 9, "Leaky Bucket: 2Mb"),
        (9, 10, "Bottleneck: 3.5Mb, 20ms"),
    ]

    fig, ax = plt.subplots(figsize=(12, 7))

    # Draw edges
    for u, v, label in edges:
        p1 = pos[u]
        p2 = pos[v]
        is_bottleneck = (u == 9 and v == 10)
        is_shaper = (u == 8 and v == 9)
        edge_color = "red" if is_bottleneck else ("green" if is_shaper else "#7f8c8d")
        style = "--" if is_shaper else "-"
        width = 3.0 if is_bottleneck else (2.2 if is_shaper else 1.5)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=edge_color, linestyle=style, linewidth=width, zorder=1)
        
        # Edge label
        mid_x = (p1[0] + p2[0]) / 2.0
        mid_y = (p1[1] + p2[1]) / 2.0
        if is_bottleneck:
            ax.text(mid_x, mid_y + 0.25, label, fontsize=9, color="darkred", fontweight="bold", ha="center")
        elif is_shaper:
            ax.text(mid_x, mid_y - 0.25, label, fontsize=9, color="darkgreen", fontweight="bold", ha="center")

    # Draw nodes
    for nid, data in nodes.items():
        x, y = pos[nid]
        ax.scatter(x, y, s=800, c=data["color"], edgecolors="black", linewidths=1.5, zorder=2)
        ax.text(x, y - 0.45, data["label"], fontsize=8.5, ha="center", va="top", fontweight="bold")

    ax.set_title("Smart City Network Simulation Topology & Queue Bottleneck", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlim(-1.2, 8.8)
    ax.set_ylim(-2.0, 6.0)
    ax.axis("off")

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, "5_network_topology.png"), dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    generate_all_plots()
