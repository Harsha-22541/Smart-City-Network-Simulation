"""
==============================================================================
Leaky Bucket Traffic Shaping & Buffer Management Implementation
Project: Smart City Network Simulation and Congestion Analysis
Description:
    Models the Leaky Bucket algorithm used to police and shape bursty IoT
    and CCTV transmission streams. Calculates buffer utilization, packet drops,
    data rate, and throughput under varying city traffic conditions.
==============================================================================
"""

import sys
import time
from typing import List, Dict, Tuple

class LeakyBucket:
    """
    Simulates a finite-buffer Leaky Bucket traffic shaper.
    
    Attributes:
        capacity (float): Maximum buffer capacity (in packets or bytes).
        leak_rate (float): Constant rate at which buffer is drained (units/sec).
        current_buffer (float): Current amount stored in buffer.
        total_arrived (float): Cumulative units received.
        total_leaked (float): Cumulative units transmitted downstream.
        total_dropped (float): Cumulative units lost due to buffer overflow.
    """
    def __init__(self, capacity: float, leak_rate: float):
        self.capacity = float(capacity)
        self.leak_rate = float(leak_rate)
        self.current_buffer = 0.0
        self.total_arrived = 0.0
        self.total_leaked = 0.0
        self.total_dropped = 0.0
        self.history: List[Dict[str, float]] = []

    def process_arrival(self, time_sec: float, incoming_packets: float, duration_sec: float = 1.0) -> Dict[str, float]:
        """
        Process an arrival event over a time interval.
        """
        self.total_arrived += incoming_packets
        
        # 1. Check buffer admission
        available_space = self.capacity - self.current_buffer
        if incoming_packets <= available_space:
            accepted = incoming_packets
            dropped = 0.0
            self.current_buffer += incoming_packets
        else:
            accepted = available_space
            dropped = incoming_packets - available_space
            self.current_buffer = self.capacity
            self.total_dropped += dropped

        # 2. Constant leak during this time window
        drain_potential = self.leak_rate * duration_sec
        if self.current_buffer >= drain_potential:
            leaked = drain_potential
            self.current_buffer -= drain_potential
        else:
            leaked = self.current_buffer
            self.current_buffer = 0.0

        self.total_leaked += leaked
        buffer_util = (self.current_buffer / self.capacity) * 100.0 if self.capacity > 0 else 0.0

        record = {
            "time": time_sec,
            "incoming": incoming_packets,
            "accepted": accepted,
            "dropped": dropped,
            "leaked": leaked,
            "buffer_rem": self.current_buffer,
            "buffer_util_pct": buffer_util
        }
        self.history.append(record)
        return record

    def run_simulation(self, traffic_pattern: List[float], time_step: float = 1.0) -> Dict[str, float]:
        """
        Simulate traffic over time sequence.
        """
        self.history.clear()
        self.current_buffer = 0.0
        self.total_arrived = 0.0
        self.total_leaked = 0.0
        self.total_dropped = 0.0

        t = 1.0
        for incoming in traffic_pattern:
            self.process_arrival(t, incoming, time_step)
            t += time_step

        # Drain any residual packets left in buffer
        while self.current_buffer > 0.001:
            self.process_arrival(t, 0.0, time_step)
            t += time_step

        drop_rate = (self.total_dropped / self.total_arrived * 100.0) if self.total_arrived > 0 else 0.0
        throughput = (self.total_leaked / len(self.history)) if self.history else 0.0

        return {
            "total_arrived": self.total_arrived,
            "total_leaked": self.total_leaked,
            "total_dropped": self.total_dropped,
            "drop_rate_pct": drop_rate,
            "average_throughput": throughput,
            "total_duration": len(self.history) * time_step
        }

    def print_table(self):
        """Prints a formatted ASCII execution trace table."""
        print("=" * 86)
        print("                   SMART CITY LEAKY BUCKET EXECUTION TRACE                   ")
        print("=" * 86)
        print(f" Buffer Capacity: {self.capacity:.0f} pkts | Constant Outflow Leak Rate: {self.leak_rate:.0f} pkts/s")
        print("-" * 86)
        print("Time  | Arriving  | Accepted  | Dropped   | Transmitted | Remaining  | Buffer Util")
        print("(sec) | (Packets) | (Buffer)  | (Drops)   | (Outflow)   | in Buffer  | (%)")
        print("------+-----------+-----------+-----------+-------------+------------+------------")
        for r in self.history:
            print(f"{r['time']:5.1f} | {r['incoming']:9.1f} | {r['accepted']:9.1f} | "
                  f"{r['dropped']:9.1f} | {r['leaked']:11.1f} | {r['buffer_rem']:10.1f} | "
                  f"{r['buffer_util_pct']:9.2f}%")
        print("=" * 86)
        summary = {
            "total_arrived": self.total_arrived,
            "total_leaked": self.total_leaked,
            "total_dropped": self.total_dropped,
            "drop_rate_pct": (self.total_dropped / self.total_arrived * 100.0) if self.total_arrived > 0 else 0.0
        }
        print(" SUMMARY METRICS:")
        print(f"  * Total Packets Injected     : {summary['total_arrived']:.0f}")
        print(f"  * Total Successfully Leaked  : {summary['total_leaked']:.0f}")
        print(f"  * Total Buffer Drops (Loss)  : {summary['total_dropped']:.0f}")
        print(f"  * Packet Drop Percentage     : {summary['drop_rate_pct']:.2f}%")
        print("=" * 86)

if __name__ == "__main__":
    # Test with typical smart city traffic burst sequence:
    # CCTV high bursts (t=2..4) and emergency burst (t=7)
    sample_traffic = [4, 10, 18, 15, 6, 3, 20, 5, 2, 0]
    
    print("\n--- TEST CASE 1: Standard Buffer (Capacity=20, Leak Rate=5) ---")
    lb1 = LeakyBucket(capacity=20, leak_rate=5)
    lb1.run_simulation(sample_traffic)
    lb1.print_table()

    print("\n--- TEST CASE 2: Constrained Buffer (Capacity=10, Leak Rate=5) ---")
    lb2 = LeakyBucket(capacity=10, leak_rate=5)
    lb2.run_simulation(sample_traffic)
    lb2.print_table()
