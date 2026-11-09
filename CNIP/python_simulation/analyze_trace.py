"""
==============================================================================
NS-2 Trace File Analyzer (Python Equivalent of AWK Scripts)
Project: Smart City Network Simulation and Congestion Analysis
Description:
    Parses NS-2 format trace files (.tr) to compute:
    1. Average and instantaneous throughput (equivalent to throughput.awk)
    2. Packet drop statistics and categories (equivalent to packet_drop.awk)
    3. Packet Delivery Ratio (equivalent to pdr.awk)
    4. End-to-End Transmission Delay (equivalent to delay.awk)
    5. Bottleneck Buffer Utilization (equivalent to buffer_utilization.awk)
Usage:
    python analyze_trace.py <path_to_trace_file> [destination_node]
==============================================================================
"""

import sys
import os

def analyze_trace_file(trace_path: str, dest_node: int = 10):
    if not os.path.exists(trace_path):
        print(f"Error: Trace file not found at '{trace_path}'")
        return

    print("=" * 70)
    print(f"               NS-2 TRACE ANALYSIS REPORT               ")
    print(f" Trace File: {os.path.basename(trace_path)}")
    print("=" * 70)

    total_sent = 0
    total_received = 0
    total_dropped = 0
    total_bytes_received = 0
    start_time = float("inf")
    stop_time = 0.0

    flow_sent = {}
    flow_dropped = {}
    flow_received = {}
    node_drops = {}

    send_times = {}
    delays = []

    curr_q = 0
    max_q = 0
    sum_q = 0
    q_samples = 0

    with open(trace_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 12:
                continue

            event = parts[0]
            try:
                time = float(parts[1])
                from_node = int(parts[2])
                to_node = int(parts[3])
                pkt_type = parts[4]
                pkt_size = int(parts[5])
                flow_id = int(parts[7])
                pkt_id = int(parts[11])
            except (ValueError, IndexError):
                continue

            # Track start and stop time
            if event == "+" and from_node < 7:
                total_sent += 1
                flow_sent[flow_id] = flow_sent.get(flow_id, 0) + 1
                send_times[pkt_id] = time

            if event == "r" and to_node == dest_node:
                total_received += 1
                total_bytes_received += pkt_size
                flow_received[flow_id] = flow_received.get(flow_id, 0) + 1
                if time < start_time:
                    start_time = time
                if time > stop_time:
                    stop_time = time

                if pkt_id in send_times:
                    delay = time - send_times[pkt_id]
                    delays.append(delay)

            if event == "d":
                total_dropped += 1
                flow_dropped[flow_id] = flow_dropped.get(flow_id, 0) + 1
                node_drops[from_node] = node_drops.get(from_node, 0) + 1

            # Monitor bottleneck queue (Node 9 -> 10)
            if from_node == 9 and to_node == 10:
                if event == "+":
                    curr_q += 1
                    if curr_q > max_q:
                        max_q = curr_q
                elif event == "-":
                    if curr_q > 0:
                        curr_q -= 1
                sum_q += curr_q
                q_samples += 1

    # 1. Throughput Calculation
    duration = stop_time - start_time if stop_time > start_time else 0.001
    throughput_kbps = (total_bytes_received * 8.0) / (duration * 1000.0)
    throughput_mbps = throughput_kbps / 1000.0

    print(" 1. THROUGHPUT & VOLUME SUMMARY:")
    print(f"    - Monitoring Duration     : {start_time:.2f}s to {stop_time:.2f}s ({duration:.2f} seconds)")
    print(f"    - Total Data Received     : {total_bytes_received / (1024 * 1024):.2f} MB ({total_bytes_received / 1024:.2f} KB)")
    print(f"    - Average Throughput      : {throughput_kbps:.2f} Kbps ({throughput_mbps:.3f} Mbps)")

    # 2. Packet Delivery Ratio (PDR)
    pdr = (total_received / total_sent * 100.0) if total_sent > 0 else 0.0
    drop_pct = (total_dropped / total_sent * 100.0) if total_sent > 0 else 0.0
    print("\n 2. PACKET DELIVERY RATIO & DROP RATE:")
    print(f"    - Total Packets Injected  : {total_sent}")
    print(f"    - Successfully Delivered  : {total_received}")
    print(f"    - Total Packets Dropped   : {total_dropped}")
    print(f"    - Packet Delivery Ratio   : {pdr:.2f}%")
    print(f"    - Packet Loss Ratio       : {drop_pct:.2f}%")

    # 3. Flow-by-flow Breakdown
    print("\n 3. FLOW-LEVEL BREAKDOWN:")
    print("    Flow ID | Category              | Enqueued | Delivered | Dropped | Drop Rate")
    print("    --------+-----------------------+----------+-----------+---------+----------")
    categories = {
        1: "Traffic Signals",
        2: "CCTV Surveillance",
        3: "Pollution Sensor",
        4: "Smart Lighting",
        5: "Emergency Service"
    }
    for fid in sorted(flow_sent.keys()):
        cat = categories.get(fid, f"Flow {fid}")
        sent = flow_sent[fid]
        recv = flow_received.get(fid, 0)
        drop = flow_dropped.get(fid, 0)
        rate = (drop / sent * 100.0) if sent > 0 else 0.0
        print(f"    {fid:<7} | {cat:<21} | {sent:<8} | {recv:<9} | {drop:<7} | {rate:6.2f}%")

    # 4. Latency / Delay Analysis
    print("\n 4. TRANSMISSION DELAY (LATENCY):")
    if delays:
        avg_delay_ms = (sum(delays) / len(delays)) * 1000.0
        min_delay_ms = min(delays) * 1000.0
        max_delay_ms = max(delays) * 1000.0
        print(f"    - Average End-to-End Delay: {avg_delay_ms:.2f} ms")
        print(f"    - Min End-to-End Delay    : {min_delay_ms:.2f} ms")
        print(f"    - Max End-to-End Delay    : {max_delay_ms:.2f} ms")
    else:
        print("    - No round-trip delay data available.")

    # 5. Bottleneck Buffer Utilization
    print("\n 5. BOTTLENECK BUFFER UTILIZATION (Node 9 -> 10):")
    avg_q = (sum_q / q_samples) if q_samples > 0 else 0.0
    print(f"    - Peak Queue Length       : {max_q} packets")
    print(f"    - Average Queue Length    : {avg_q:.2f} packets")
    for node, count in node_drops.items():
        print(f"    - Router Node {node} Overflow Drops : {count} packets")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        trace_file = sys.argv[1]
    else:
        # Default to sample baseline trace
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        trace_file = os.path.join(base_dir, "results", "trace_samples", "smart_city_baseline.tr")
    
    analyze_trace_file(trace_file)
