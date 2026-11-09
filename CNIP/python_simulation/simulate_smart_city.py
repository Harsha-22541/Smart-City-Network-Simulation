"""
==============================================================================
Smart City Discrete-Event Network Simulation Engine
Project: Smart City Network Simulation and Congestion Analysis
Description:
    Models end-to-end packet dynamics in a Smart City network:
    - Devices: Traffic Signals, CCTV Cameras, Sensors, Street Lights, Emergency
    - Network Architecture: Edge aggregation routers, Core bottleneck gateway, Central TMC
    - Congestion Scenarios: Baseline (DropTail) vs Leaky Bucket Shaping
    - Protocol Analysis: TCP (AIMD congestion control) vs UDP (unregulated CBR)
    - Generates NS-2 compatible trace files (.tr) and metric arrays for plotting
==============================================================================
"""

import os
import math
import random
from typing import List, Dict, Any, Tuple

# Set fixed random seed for reproducible research
random.seed(42)

class Packet:
    def __init__(self, pkt_id: int, time_created: float, src_id: int, dst_id: int, 
                 flow_id: int, flow_name: str, size_bytes: int, protocol: str):
        self.pkt_id = pkt_id
        self.time_created = time_created
        self.src_id = src_id
        self.dst_id = dst_id
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.size_bytes = size_bytes
        self.protocol = protocol
        self.status = "enqueued" # 'enqueued', 'dropped', 'delivered'
        self.time_delivered = None
        self.drop_reason = None

class SmartCitySimulator:
    def __init__(self, sim_duration: float = 10.0, time_step: float = 0.05):
        self.duration = sim_duration
        self.dt = time_step
        self.time_points = [round(i * self.dt, 3) for i in range(int(sim_duration / self.dt) + 1)]

        # Device Definitions
        self.devices = {
            0: {"name": "Traffic_Signal_1", "category": "Signal", "proto": "UDP", "rate_kbps": 400, "pkt_size": 512, "start": 0.5, "stop": 9.0},
            1: {"name": "Traffic_Signal_2", "category": "Signal", "proto": "UDP", "rate_kbps": 400, "pkt_size": 512, "start": 0.7, "stop": 9.0},
            2: {"name": "CCTV_Camera_1",    "category": "CCTV",   "proto": "UDP", "rate_kbps": 2800, "pkt_size": 1024, "start": 1.5, "stop": 8.5},
            3: {"name": "CCTV_Camera_2",    "category": "CCTV",   "proto": "UDP", "rate_kbps": 2500, "pkt_size": 1024, "start": 2.0, "stop": 8.0},
            4: {"name": "Pollution_Sensor", "category": "Sensor", "proto": "UDP", "rate_kbps": 150, "pkt_size": 256,  "start": 1.0, "stop": 9.5},
            5: {"name": "Smart_Lighting",   "category": "Light",  "proto": "UDP", "rate_kbps": 120, "pkt_size": 256,  "start": 1.2, "stop": 9.5},
            6: {"name": "Emergency_Service","category": "Alert",  "proto": "UDP", "rate_kbps": 1500, "pkt_size": 1024, "start": 3.0, "stop": 7.0},
        }

    def run_scenario(self, use_leaky_bucket: bool = False, buffer_capacity: int = 15, bottleneck_mbps: float = 3.5) -> Dict[str, Any]:
        """
        Runs network simulation under either Uncontrolled (DropTail) or Leaky Bucket Traffic Shaper mode.
        """
        # Bottleneck link drain rate in bytes per time step
        bottleneck_bytes_per_step = (bottleneck_mbps * 1e6 / 8.0) * self.dt
        
        # Leaky bucket shaper for high-burst CCTV feeds (Node 8)
        shaper_buffer_cap = 40 # packets
        shaper_current_buf: List[Packet] = []
        shaper_leak_bytes_step = (2.0 * 1e6 / 8.0) * self.dt # 2.0 Mbps leak rate

        # Core Gateway Bottleneck queue (Node 9 -> Node 10)
        gateway_queue: List[Packet] = []
        
        # Metrics logs
        throughput_log = []
        buffer_occupancy_log = []
        packet_drops_log = []
        delivered_log = []
        time_series = []

        all_packets: List[Packet] = []
        pkt_counter = 0

        trace_records = []

        # Flow tracking
        flow_sent = {fid: 0 for fid in range(1, 7)}
        flow_dropped = {fid: 0 for fid in range(1, 7)}
        flow_delivered = {fid: 0 for fid in range(1, 7)}

        for t in self.time_points:
            time_series.append(t)
            step_incoming_packets: List[Packet] = []

            # 1. Traffic Generation from Smart City Devices
            for dev_id, dev in self.devices.items():
                if dev["start"] <= t <= dev["stop"]:
                    # Rate adjustment in Leaky Bucket scenario for smoothed streams
                    rate_kbps = dev["rate_kbps"]
                    if use_leaky_bucket and dev["category"] == "CCTV":
                        rate_kbps = rate_kbps * 0.45  # Regulated video stream

                    # Calculate expected packets in this dt step
                    expected_pkts = (rate_kbps * 1000 / 8.0 / dev["pkt_size"]) * self.dt
                    # Poisson / jitter arrival
                    num_pkts = int(expected_pkts)
                    if random.random() < (expected_pkts - num_pkts):
                        num_pkts += 1

                    for _ in range(num_pkts):
                        pkt_counter += 1
                        fid = 2 if dev["category"] == "CCTV" else (1 if dev["category"] == "Signal" else (3 if dev["category"] == "Sensor" else (4 if dev["category"] == "Light" else 5)))
                        p = Packet(
                            pkt_id=pkt_counter,
                            time_created=t,
                            src_id=dev_id,
                            dst_id=10,
                            flow_id=fid,
                            flow_name=dev["name"],
                            size_bytes=dev["pkt_size"],
                            protocol=dev["proto"]
                        )
                        all_packets.append(p)
                        step_incoming_packets.append(p)
                        flow_sent[fid] = flow_sent.get(fid, 0) + 1
                        # NS-2 enqueue trace: + time from to type size flags fid src.port dst.port seq pktid
                        trace_records.append(f"+ {t:.4f} {dev_id} 7 cbr {p.size_bytes} ------- {fid} {dev_id}.0 10.0 {pkt_counter} {pkt_counter}")

            step_drops = 0
            packets_to_gateway: List[Packet] = []

            # 2. Edge Routing & Optional Leaky Bucket Shaping
            if use_leaky_bucket:
                for p in step_incoming_packets:
                    if p.flow_id == 2: # CCTV flows pass through Leaky Bucket Shaper
                        if len(shaper_current_buf) < shaper_buffer_cap:
                            shaper_current_buf.append(p)
                        else:
                            p.status = "dropped"
                            p.drop_reason = "shaper_overflow"
                            flow_dropped[p.flow_id] = flow_dropped.get(p.flow_id, 0) + 1
                            step_drops += 1
                            trace_records.append(f"d {t:.4f} 8 9 cbr {p.size_bytes} ------- {p.flow_id} {p.src_id}.0 10.0 {p.pkt_id} {p.pkt_id}")
                    else:
                        packets_to_gateway.append(p)

                # Leak out of shaper at constant rate
                bytes_leaked = 0
                while shaper_current_buf and (bytes_leaked + shaper_current_buf[0].size_bytes <= shaper_leak_bytes_step):
                    pkt = shaper_current_buf.pop(0)
                    bytes_leaked += pkt.size_bytes
                    packets_to_gateway.append(pkt)
            else:
                packets_to_gateway = step_incoming_packets

            # 3. Admission to Bottleneck Gateway (Node 9 -> 10)
            for p in packets_to_gateway:
                if len(gateway_queue) < buffer_capacity:
                    gateway_queue.append(p)
                    trace_records.append(f"+ {t:.4f} 9 10 cbr {p.size_bytes} ------- {p.flow_id} {p.src_id}.0 10.0 {p.pkt_id} {p.pkt_id}")
                else:
                    # Buffer overflow drop
                    p.status = "dropped"
                    p.drop_reason = "bottleneck_buffer_overflow"
                    flow_dropped[p.flow_id] = flow_dropped.get(p.flow_id, 0) + 1
                    step_drops += 1
                    trace_records.append(f"d {t:.4f} 9 10 cbr {p.size_bytes} ------- {p.flow_id} {p.src_id}.0 10.0 {p.pkt_id} {p.pkt_id}")

            # 4. Transmission across bottleneck link to Central TMC Server (Node 10)
            step_bytes_delivered = 0
            while gateway_queue and (step_bytes_delivered + gateway_queue[0].size_bytes <= bottleneck_bytes_per_step):
                p = gateway_queue.pop(0)
                p.status = "delivered"
                p.time_delivered = t + 0.02 # 20ms link delay
                step_bytes_delivered += p.size_bytes
                flow_delivered[p.flow_id] = flow_delivered.get(p.flow_id, 0) + 1
                trace_records.append(f"- {t:.4f} 9 10 cbr {p.size_bytes} ------- {p.flow_id} {p.src_id}.0 10.0 {p.pkt_id} {p.pkt_id}")
                trace_records.append(f"r {(t + 0.02):.4f} 9 10 cbr {p.size_bytes} ------- {p.flow_id} {p.src_id}.0 10.0 {p.pkt_id} {p.pkt_id}")

            # Record metrics
            step_throughput_kbps = (step_bytes_delivered * 8.0) / (self.dt * 1000.0)
            throughput_log.append(step_throughput_kbps)
            buffer_occupancy_log.append(len(gateway_queue))
            packet_drops_log.append(step_drops)
            delivered_log.append(len(gateway_queue))

        total_sent = sum(flow_sent.values())
        total_dropped = sum(flow_dropped.values())
        total_delivered = sum(flow_delivered.values())
        pdr = (total_delivered / total_sent * 100.0) if total_sent > 0 else 0.0
        avg_throughput = sum(throughput_log) / len(throughput_log) if throughput_log else 0.0

        return {
            "time_series": time_series,
            "throughput_log": throughput_log,
            "buffer_occupancy_log": buffer_occupancy_log,
            "packet_drops_log": packet_drops_log,
            "total_sent": total_sent,
            "total_dropped": total_dropped,
            "total_delivered": total_delivered,
            "pdr": pdr,
            "avg_throughput_kbps": avg_throughput,
            "flow_sent": flow_sent,
            "flow_dropped": flow_dropped,
            "flow_delivered": flow_delivered,
            "trace_records": trace_records
        }

    def simulate_tcp_vs_udp(self) -> Dict[str, Any]:
        """
        Simulates TCP (AIMD congestion control) vs UDP (unregulated CBR)
        competing over the bottleneck link.
        """
        bottleneck_rate_kbps = 2000.0 # 2.0 Mbps
        buffer_size = 15 # packets

        time_series = []
        tcp_cwnd_log = []
        tcp_throughput_log = []
        udp_throughput_log = []
        queue_len_log = []

        # TCP state (NewReno model)
        cwnd = 1.0 # packets
        ssthresh = 16.0
        rtt = 0.04 # 40ms round-trip time

        # UDP rate: 2.5 Mbps active from t=2.0 to t=6.5
        udp_rate_kbps = 2500.0

        current_queue = 0
        pkt_size = 1024 # bytes (8192 bits)

        for t in self.time_points:
            time_series.append(t)

            # Determine UDP incoming traffic
            udp_active = (2.0 <= t <= 6.5)
            udp_bits_step = (udp_rate_kbps * 1000 * self.dt) if udp_active else 0
            udp_pkts = int(udp_bits_step / (pkt_size * 8))

            # Determine TCP incoming traffic based on cwnd
            # In each RTT, cwnd packets are sent
            tcp_pkts_rate = (cwnd * pkt_size * 8) / rtt # bits per second
            tcp_bits_step = tcp_pkts_rate * self.dt
            tcp_pkts = int(tcp_bits_step / (pkt_size * 8))

            # Packets arriving at bottleneck queue
            incoming_total = udp_pkts + tcp_pkts
            current_queue += incoming_total

            # Service rate of bottleneck
            service_pkts = int((bottleneck_rate_kbps * 1000 * self.dt) / (pkt_size * 8))
            
            # Check overflow
            tcp_drop = False
            if current_queue > buffer_size:
                excess = current_queue - buffer_size
                current_queue = buffer_size
                # If congestion occurs, TCP experiences packet drop
                if tcp_pkts > 0:
                    tcp_drop = True

            # Drain queue
            served = min(current_queue, service_pkts)
            current_queue -= served

            # Partition served throughput
            if incoming_total > 0:
                tcp_share = (tcp_pkts / incoming_total) * served * (pkt_size * 8) / (self.dt * 1000)
                udp_share = (udp_pkts / incoming_total) * served * (pkt_size * 8) / (self.dt * 1000)
            else:
                tcp_share = 0.0
                udp_share = 0.0

            # TCP AIMD dynamics update
            if t >= 0.5 and t <= 9.0:
                if tcp_drop:
                    # Multiplicative Decrease
                    ssthresh = max(2.0, cwnd / 2.0)
                    cwnd = max(1.0, cwnd / 2.0)
                else:
                    # Additive Increase or Slow Start
                    if cwnd < ssthresh:
                        # Slow start: exponential growth
                        cwnd += 1.0 * (self.dt / rtt)
                    else:
                        # Congestion avoidance: additive linear increase
                        cwnd += (1.0 / cwnd) * (self.dt / rtt)
            else:
                cwnd = 1.0

            tcp_cwnd_log.append(cwnd)
            tcp_throughput_log.append(tcp_share)
            udp_throughput_log.append(udp_share)
            queue_len_log.append(current_queue)

        return {
            "time_series": time_series,
            "tcp_cwnd": tcp_cwnd_log,
            "tcp_throughput": tcp_throughput_log,
            "udp_throughput": udp_throughput_log,
            "queue_len": queue_len_log
        }

if __name__ == "__main__":
    sim = SmartCitySimulator()
    print("Executing Baseline Simulation...")
    res_base = sim.run_scenario(use_leaky_bucket=False, buffer_capacity=15)
    print(f"Baseline -> Sent: {res_base['total_sent']}, Dropped: {res_base['total_dropped']}, PDR: {res_base['pdr']:.2f}%")

    print("\nExecuting Leaky Bucket Simulation...")
    res_lb = sim.run_scenario(use_leaky_bucket=True, buffer_capacity=30)
    print(f"Leaky Bucket -> Sent: {res_lb['total_sent']}, Dropped: {res_lb['total_dropped']}, PDR: {res_lb['pdr']:.2f}%")
