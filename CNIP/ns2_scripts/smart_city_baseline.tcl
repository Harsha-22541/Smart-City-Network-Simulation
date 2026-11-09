# ==============================================================================
# Smart City Network Simulation: Baseline Congestion Scenario (Uncontrolled)
# Project: Smart City Network Simulation and Congestion Analysis
# Description: Demonstrates buffer overflow, packet drops, and throughput
#              degradation when multiple smart city IoT devices and CCTV feeds
#              transmit simultaneously without traffic shaping (DropTail queue).
# Tool: NS-2 (Network Simulator 2)
# ==============================================================================

# Create a Simulator object
set ns [new Simulator]

# Define visualization colors for NAM
$ns color 1 Blue       ;# Traffic Signals
$ns color 2 Red        ;# CCTV High-Bandwidth Video Feeds
$ns color 3 Green      ;# Pollution & Environmental Sensors
$ns color 4 Orange     ;# Smart Street Lights
$ns color 5 Purple     ;# Emergency Services Priority Traffic

# Open the Trace and NAM files
set tracefile [open "smart_city_baseline.tr" w]
$ns trace-all $tracefile

set namfile [open "smart_city_baseline.nam" w]
$ns namtrace-all $namfile

# Define the 'finish' procedure
proc finish {} {
    global ns tracefile namfile
    $ns flush-trace
    close $tracefile
    close $namfile
    puts "=========================================================="
    puts " Baseline Simulation Finished Successfully!"
    puts " Output trace generated : smart_city_baseline.tr"
    puts " Output NAM generated   : smart_city_baseline.nam"
    puts " Run 'nam smart_city_baseline.nam' to visualize network"
    puts "=========================================================="
    exit 0
}

# ==============================================================================
# Node Creation (Smart City Infrastructure)
# ==============================================================================
# IoT Sources & Edge End-devices
set n0 [$ns node]   ;# Traffic Signal 1
set n1 [$ns node]   ;# Traffic Signal 2
set n2 [$ns node]   ;# CCTV Surveillance Camera 1 (High Rate)
set n3 [$ns node]   ;# CCTV Surveillance Camera 2 (High Rate)
set n4 [$ns node]   ;# Pollution & Air Quality Sensor
set n5 [$ns node]   ;# Smart Street Lighting Controller
set n6 [$ns node]   ;# Emergency Services & First Responders

# Aggregation & Core Routing Nodes
set n7 [$ns node]   ;# Edge Aggregation Router 1 (IoT & Signals)
set n8 [$ns node]   ;# Edge Aggregation Router 2 (CCTV & Video Feeds)
set n9 [$ns node]   ;# Central Gateway / Bottleneck Core Router

# Central Destination
set n10 [$ns node]  ;# Central Traffic Management Center (TMC) & Cloud Control

# ==============================================================================
# Node Labeling and Visual Appearance in NAM
# ==============================================================================
$n0 label "Traffic_Signal_1"
$n1 label "Traffic_Signal_2"
$n2 label "CCTV_Camera_1"
$n3 label "CCTV_Camera_2"
$n4 label "Pollution_Sensor"
$n5 label "Smart_Lighting"
$n6 label "Emergency_Service"
$n7 label "Edge_Router_IoT"
$n8 label "Edge_Router_CCTV"
$n9 label "Core_Gateway_Bottleneck"
$n10 label "Central_TMC_Server"

$n0 shape box; $n1 shape box
$n2 shape circle; $n3 shape circle
$n4 shape hexagon; $n5 shape hexagon
$n6 shape doublecircle
$n7 shape square; $n8 shape square
$n9 shape square
$n10 shape box

$n0 color blue; $n1 color blue
$n2 color red; $n3 color red
$n4 color green; $n5 color orange
$n6 color purple
$n7 color black; $n8 color black
$n9 color brown
$n10 color navy

# ==============================================================================
# Network Links & Topology Setup
# ==============================================================================
# Edge Links (Access Network): Bandwidth, Delay, Queue Type
$ns duplex-link $n0 $n7 5Mb 2ms DropTail
$ns duplex-link $n1 $n7 5Mb 2ms DropTail
$ns duplex-link $n4 $n7 2Mb 5ms DropTail
$ns duplex-link $n5 $n7 2Mb 5ms DropTail

$ns duplex-link $n2 $n8 10Mb 2ms DropTail
$ns duplex-link $n3 $n8 10Mb 2ms DropTail
$ns duplex-link $n6 $n8 10Mb 1ms DropTail

# Distribution Links to Core Gateway
$ns duplex-link $n7 $n9 8Mb 5ms DropTail
$ns duplex-link $n8 $n9 10Mb 5ms DropTail

# Bottleneck Link: Central Gateway (n9) -> Central TMC Server (n10)
# Limited capacity (3.5 Mbps) and finite queue buffer (15 packets)
$ns duplex-link $n9 $n10 3.5Mb 20ms DropTail
$ns queue-limit $n9 $n10 15

# Set link orientations for organized NAM layout
$ns duplex-link-op $n0 $n7 orient right-down
$ns duplex-link-op $n1 $n7 orient right
$ns duplex-link-op $n4 $n7 orient right-up
$ns duplex-link-op $n5 $n7 orient up

$ns duplex-link-op $n2 $n8 orient right-down
$ns duplex-link-op $n3 $n8 orient right
$ns duplex-link-op $n6 $n8 orient right-up

$ns duplex-link-op $n7 $n9 orient right-down
$ns duplex-link-op $n8 $n9 orient right-up
$ns duplex-link-op $n9 $n10 orient right

# Monitor queue on the bottleneck link
$ns duplex-link-op $n9 $n10 queuePos 0.5

# ==============================================================================
# Traffic Generators & Protocol Agents (Simulating Bursty Smart City Load)
# ==============================================================================

# Destination Null Agent at Central TMC Server (Node 10)
set null0 [new Agent/Null]
$ns attach-agent $n10 $null0

# Flow 1: Traffic Signal 1 (Telemetry & Cycle Status)
set udp0 [new Agent/UDP]
$udp0 set class_ 1
$udp0 set fid_ 1
$ns attach-agent $n0 $udp0
$ns connect $udp0 $null0
set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 512
$cbr0 set rate_ 400Kb
$cbr0 set random_ 1
$cbr0 attach-agent $udp0

# Flow 2: Traffic Signal 2
set udp1 [new Agent/UDP]
$udp1 set class_ 1
$udp1 set fid_ 1
$ns attach-agent $n1 $udp1
$ns connect $udp1 $null0
set cbr1 [new Application/Traffic/CBR]
$cbr1 set packetSize_ 512
$cbr1 set rate_ 400Kb
$cbr1 set random_ 1
$cbr1 attach-agent $udp1

# Flow 3: CCTV Camera 1 (High Bandwidth Video Stream - Heavy Burst)
set udp2 [new Agent/UDP]
$udp2 set class_ 2
$udp2 set fid_ 2
$ns attach-agent $n2 $udp2
$ns connect $udp2 $null0
set cbr2 [new Application/Traffic/CBR]
$cbr2 set packetSize_ 1024
$cbr2 set rate_ 2.8Mb
$cbr2 set random_ 1
$cbr2 attach-agent $udp2

# Flow 4: CCTV Camera 2 (High Bandwidth Video Stream - Peak Burst)
set udp3 [new Agent/UDP]
$udp3 set class_ 2
$udp3 set fid_ 2
$ns attach-agent $n3 $udp3
$ns connect $udp3 $null0
set cbr3 [new Application/Traffic/CBR]
$cbr3 set packetSize_ 1024
$cbr3 set rate_ 2.5Mb
$cbr3 set random_ 1
$cbr3 attach-agent $udp3

# Flow 5: Pollution & Environmental Sensor (Periodic telemetry)
set udp4 [new Agent/UDP]
$udp4 set class_ 3
$udp4 set fid_ 3
$ns attach-agent $n4 $udp4
$ns connect $udp4 $null0
set cbr4 [new Application/Traffic/CBR]
$cbr4 set packetSize_ 256
$cbr4 set rate_ 150Kb
$cbr4 set random_ 1
$cbr4 attach-agent $udp4

# Flow 6: Smart Street Lighting Controller
set udp5 [new Agent/UDP]
$udp5 set class_ 4
$udp5 set fid_ 4
$ns attach-agent $n5 $udp5
$ns connect $udp5 $null0
set cbr5 [new Application/Traffic/CBR]
$cbr5 set packetSize_ 256
$cbr5 set rate_ 120Kb
$cbr5 set random_ 1
$cbr5 attach-agent $udp5

# Flow 7: Emergency Services (Ambulance / Fire Alert Burst)
set udp6 [new Agent/UDP]
$udp6 set class_ 5
$udp6 set fid_ 5
$ns attach-agent $n6 $udp6
$ns connect $udp6 $null0
set cbr6 [new Application/Traffic/CBR]
$cbr6 set packetSize_ 1024
$cbr6 set rate_ 1.5Mb
$cbr6 set random_ 1
$cbr6 attach-agent $udp6

# ==============================================================================
# Simulation Event Scheduling
# ==============================================================================
# Normal smart city operations start
$ns at 0.5 "$cbr0 start"
$ns at 0.7 "$cbr1 start"
$ns at 1.0 "$cbr4 start"
$ns at 1.2 "$cbr5 start"

# Heavy video streams start, creating load
$ns at 1.5 "$cbr2 start"
$ns at 2.0 "$cbr3 start"

# Emergency alert triggered during peak traffic (causes severe congestion & drops)
$ns at 3.0 "$cbr6 start"
$ns at 7.0 "$cbr6 stop"

# CCTV video stream stops
$ns at 8.0 "$cbr3 stop"
$ns at 8.5 "$cbr2 stop"

# IoT sensors continue to the end
$ns at 9.0 "$cbr0 stop"
$ns at 9.0 "$cbr1 stop"
$ns at 9.5 "$cbr4 stop"
$ns at 9.5 "$cbr5 stop"

# Call finish after 10.0 seconds of simulation
$ns at 10.0 "finish"

# Run the simulation
$ns run
