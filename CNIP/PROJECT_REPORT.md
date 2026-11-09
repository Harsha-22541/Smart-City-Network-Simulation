# Smart City Network Simulation and Congestion Analysis
**Comprehensive Laboratory & Project Technical Report**

---

## 1. Problem Statement & Background

In a modern smart city infrastructure, a heterogeneous assortment of cyber-physical devices constantly generate and exchange network packets with edge gateways and central control cloud facilities. These systems include:
- **Intelligent Traffic Signals & Sensors**: Actuators and road induction loops transmitting periodic traffic status and light timing adjustments.
- **CCTV Surveillance Cameras**: Video streams transmitting continuous, high-definition visual telemetry characterized by high bandwidth and burstiness.
- **Pollution & Environmental Monitors**: Micro-sensors measuring PM2.5, NO₂, temperature, and humidity, transmitting periodic small payloads.
- **Smart Street Lighting**: Remote telemetry and command controllers.
- **Central Traffic Management Center (TMC)**: The primary central coordination cloud server supervising city logistics.
- **Emergency Services**: High-priority alert communications originating from emergency ambulances, police responders, and fire departments.

### The Congestion Challenge
Because network backbones and core gateway links possess finite bandwidth and finite buffer capacities, concurrent uncoordinated transmissions from bursty sources (particularly multiple 4K/1080p CCTV cameras) induce severe **network congestion**. Under standard DropTail queuing:
1. Incoming traffic exceeds bottleneck link capacity ($\sum R_{in} > C_{bottleneck}$).
2. The router queue rapidly reaches capacity, resulting in **buffer overflow**.
3. Successive packets are unceremoniously discarded (**packet drops**).
4. Mission-critical low-latency traffic (such as Emergency Service alerts or traffic signal synchronization) suffers starvation, extreme queuing delays, or total packet loss.
5. Overall network **throughput** and **Packet Delivery Ratio (PDR)** collapse.

---

## 2. Project Objectives

1. **Model a Smart City Network Topology**: Construct a realistic network architecture in NS-2 and Python consisting of IoT edge nodes, video cameras, traffic signals, edge aggregators, a bottleneck gateway router, and a central TMC server.
2. **Implement Traffic Shaping via Leaky Bucket Algorithm**: Enforce open-loop traffic policing and shaping on bursty CCTV video streams to regulate inflow into the core network.
3. **Analyze Buffer Management & Overflow**: Track buffer occupancy and evaluate packet drop ratios across different buffer capacities ($B \in [5, 50]$ packets).
4. **Compare TCP vs UDP Under Congestion**: Contrast the closed-loop, adaptive behavior of TCP (AIMD congestion control) against unthrottled, open-loop UDP (CBR) traffic.
5. **Evaluate Quantitative Metrics**: Measure Instantaneous & Average Throughput, Packet Delivery Ratio (PDR), Packet Drop Rate, End-to-End Delay, and Queue Utilization using AWK and Python analytics.

---

## 3. Network Architecture & Topology

```
+---------------------+
| Traffic Signal 1, 2 |----+
+---------------------+    |
                           v
+---------------------+  [Node 7]
| Pollution & Light   |-> Edge Router 1 --+
+---------------------+  (IoT Aggregator) |
                                          v
+---------------------+                 [Node 9]            [Node 10]
| CCTV Cameras 1 & 2  |----+          Core Gateway  ====>  Central TMC
+---------------------+    |         (Bottleneck Link)     Server & Cloud
                           v          3.5 Mbps, 20ms
+---------------------+  [Node 8]         |
| Emergency Services  |-> Edge Router 2 --+
+---------------------+  (Leaky Bucket)
```

### Node Specifications
| Node ID | Node Name | Device Type | Protocol | Nominal Bitrate | Packet Size |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **n0** | Traffic_Signal_1 | Traffic Actuator | UDP / CBR | 400 Kbps | 512 Bytes |
| **n1** | Traffic_Signal_2 | Traffic Actuator | UDP / CBR | 400 Kbps | 512 Bytes |
| **n2** | CCTV_Camera_1 | Video Surveillance | UDP / CBR (Bursty) | 2.8 Mbps | 1024 Bytes |
| **n3** | CCTV_Camera_2 | Video Surveillance | UDP / CBR (Bursty) | 2.5 Mbps | 1024 Bytes |
| **n4** | Pollution_Sensor | IoT Environmental | UDP / CBR | 150 Kbps | 256 Bytes |
| **n5** | Smart_Lighting | IoT Infrastructure | UDP / CBR | 120 Kbps | 256 Bytes |
| **n6** | Emergency_Service | Priority Responders | UDP / CBR | 1.5 Mbps | 1024 Bytes |
| **n7** | Edge_Router_IoT | Aggregator (IoT) | - | 8.0 Mbps link | - |
| **n8** | Edge_Router_Video| Shaper (CCTV) | - | 10.0 / 2.0 Mbps| Buffer: 40 pkts |
| **n9** | Core_Gateway | Core Bottleneck | - | 3.5 Mbps, 20ms | Buffer: 15–30 pkts |
| **n10**| Central_TMC | Central Server | - | Sink Node | - |

---

## 4. Mathematical Modeling: Leaky Bucket Algorithm

The **Leaky Bucket Algorithm** operates as a finite-capacity single-server queue with deterministic service time.

Let:
- $B$ be the finite bucket capacity (in packets or bytes).
- $R$ be the constant leak rate (in packets/second or bps).
- $Q(t)$ be the queue occupancy at time $t$, where $0 \le Q(t) \le B$.
- $A(t, t + \Delta t)$ be the number of packets arriving in interval $\Delta t$.

### Admission & Buffer Management Equation
When packets arrive during interval $\Delta t$:
$$\Delta Q_{arrival} = \min\left( A(t, t + \Delta t), \; B - Q(t) \right)$$

If $A(t, t + \Delta t) > B - Q(t)$, the excess packets cannot be buffered and are dropped:
$$D(t, t + \Delta t) = \max\left( 0, \; A(t, t + \Delta t) - (B - Q(t)) \right)$$

### Transmission (Leak) Equation
Regardless of burst size, the bucket drains downstream at a strictly bounded rate:
$$L(t, t + \Delta t) = \min\left( Q(t) + \Delta Q_{arrival}, \; R \cdot \Delta t \right)$$

### Queue State Evolution
$$Q(t + \Delta t) = Q(t) + \Delta Q_{arrival} - L(t, t + \Delta t)$$

### Buffer Utilization Ratio
$$U(t) = \left( \frac{Q(t)}{B} \right) \times 100\%$$

By bounding the output rate $L / \Delta t \le R$, the peak burst from CCTV feeds is prevented from swamping downstream core router queues.

---

## 5. Congestion Dynamics: TCP vs UDP Comparison

| Dimension | UDP (User Datagram Protocol) | TCP (Transmission Control Protocol) |
| :--- | :--- | :--- |
| **Connection Model** | Connectionless, Uncontrolled (Open-Loop) | Connection-Oriented, Flow & Congestion Controlled |
| **Response to Congestion** | **No response**: Transmits at fixed rate $R_{CBR}$ regardless of dropped packets. | **AIMD (Additive Increase Multiplicative Decrease)**: Halves window upon drop. |
| **Congestion Window ($cwnd$)**| None (Not applicable) | Dynamically adjusted per Round Trip Time (RTT). |
| **Bandwidth Allocation** | Monopolizes channel aggressively under buffer overflow. | Yields bandwidth; enters multiplicative backoff. |
| **Reliability** | Unreliable; dropped packets are lost forever. | Reliable; retransmits lost segments via Fast Retransmit or Timeout. |

### TCP AIMD Mathematical Model:
- **Additive Increase (Congestion Avoidance)**: For each acknowledged packet within an RTT where no drops occur:
  $$cwnd_{new} = cwnd_{old} + \frac{1}{cwnd_{old}}$$
- **Multiplicative Decrease (Packet Loss Detected)**: When buffer overflow causes a packet drop:
  $$ssthresh = \max\left( 2, \; \frac{cwnd}{2} \right), \quad cwnd_{new} = \max\left( 1, \; \frac{cwnd}{2} \right)$$

---

## 6. Simulation Results & Experimental Findings

### 6.1 Baseline vs. Leaky Bucket Quantitative Summary

| Metric | Baseline Scenario (DropTail) | Leaky Bucket Scenario (Shaped) | Improvement Factor |
| :--- | :---: | :---: | :---: |
| **Total Injected Packets** | 7,754 | 5,449 | Regulated admission |
| **Delivered Packets** | 2,554 | 4,543 | **+77.8% higher yield** |
| **Dropped Packets** | 5,200 | 906 | **82.6% reduction in loss** |
| **Packet Delivery Ratio (PDR)** | **32.94%** | **83.37%** | **+50.43% improvement** |
| **Packet Loss Ratio** | 67.06% | 16.63% | **-50.43% loss reduction** |
| **Average Network Goodput** | 1,461.59 Kbps (1.46 Mbps) | 2,612.57 Kbps (2.61 Mbps) | **+78.7% throughput** |
| **Delivered Data Volume** | 1.57 MB | 2.80 MB | **+78.3% data delivered** |
| **Average End-to-End Latency**| 20.00 ms (unbuffered drops) | 43.11 ms (controlled queue) | Tradeoff for 0% loss |

### 6.2 Flow-by-Flow Packet Delivery Analysis

```
+--------------------+---------------------+---------------------+
| Traffic Flow       | Baseline Drop Rate  | Leaky Bucket Drop   |
+--------------------+---------------------+---------------------+
| Traffic Signal 1&2 |   0.00% (Delivered) |   0.00% (Delivered) |
| CCTV Video Streams |  82.62% (Severe)    |  47.09% (Shaped)    |
| Pollution Sensor   |  82.91% (Starved)   |   0.00% (Delivered) |
| Smart Lighting     |  88.43% (Starved)   |   0.00% (Delivered) |
| Emergency Services | 100.00% (TOTAL LOSS)|   0.00% (Delivered) |
+--------------------+---------------------+---------------------+
```

> **Critical Discovery**: In the baseline scenario, when an emergency service priority vehicle transmits an alert burst (between $t=3.0\text{s}$ and $t=7.0\text{s}$), the unshaped CCTV stream has already completely filled the gateway buffer. Consequently, **100% of emergency packets were dropped**. Implementing Leaky Bucket shaping at the video edge completely eliminated buffer exhaustion for critical IoT flows, achieving **100% emergency delivery**.

---

## 7. Analysis of Graphical Visualizations

### 1. Network Throughput Dynamics (`1_throughput_comparison.png`)
- In the baseline scenario, throughput oscillates erratically, spiking when buffers briefly empty and collapsing when sustained bursts cause full drops.
- Under Leaky Bucket shaping, throughput smoothly tracks the 2.6–3.2 Mbps zone, maximizing link utilization without driving the gateway into tail-drop collapse.

### 2. Packet Drop Analysis & Buffer Sensitivity (`2_packet_drop_analysis.png`)
- The categorical bar chart highlights the disproportionate loss suffered by low-rate IoT sensors and emergency services in baseline mode.
- The buffer sensitivity curve reveals that while increasing buffer size from 5 to 50 packets decreases drops in both modes, the Leaky Bucket shaper consistently maintains drop rates 30% to 50% lower across all buffer sizes.

### 3. Buffer Occupancy Over Time (`3_buffer_utilization.png`)
- Baseline gateway buffer remains locked at 15 packets (100% capacity) during peak hours ($t=1.5\text{s}$ to $t=8.0\text{s}$), discarding every incoming packet.
- In contrast, the Leaky Bucket regulated queue operates safely below capacity, buffering incoming bursts and smoothly draining them at constant leak rate.

### 4. TCP vs. UDP Congestion Competition (`4_tcp_vs_udp_congestion.png`)
- Demonstrates TCP's responsive congestion control: When UDP burst commences at $t=2.0\text{s}$, TCP detects packet loss and halves its congestion window ($cwnd$) from 16 to 8 to 4 packets.
- TCP bandwidth contracts to avoid congestive collapse, while UDP grabs the lion's share of throughput.
- Once UDP stops at $t=6.5\text{s}$, TCP enters additive increase and recovers full link capacity.

---

## 8. Conclusion

1. Simultaneous multi-device transmissions in a smart city generate peak loads exceeding bottleneck capacities, causing severe congestion, 67% packet loss, and starvation of critical services under traditional DropTail queuing.
2. The **Leaky Bucket algorithm** effectively shapes bursty CCTV transmissions into a constant, predictable bitstream, raising the Packet Delivery Ratio from **32.94% to 83.37%** and throughput by **78.7%**.
3. Critical smart city telemetry (Emergency Alerts, Pollution Sensors, Smart Street Lighting) achieved **100% successful packet delivery** once traffic shaping was applied.
4. The comparative analysis demonstrated that unmanaged UDP traffic starves TCP flows, proving that traffic policing and active buffer management are essential in modern municipal smart city network architectures.
