# ==============================================================================
# Smart City Network Simulation: TCP vs UDP Congestion Behavior Comparison
# Project: Smart City Network Simulation and Congestion Analysis
# Description: Compares how TCP (closed-loop AIMD congestion control) and UDP
#              (open-loop unthrottled transmission) behave when competing for
#              a congested bottleneck link in a Smart City network.
# Tool: NS-2 (Network Simulator 2)
# ==============================================================================

# Create a Simulator object
set ns [new Simulator]

# Visualization colors
$ns color 1 Red     ;# UDP Flow (Unregulated CCTV/Sensors)
$ns color 2 Blue    ;# TCP Flow (Reliable TMC Control / Emergency)

# Open Trace and NAM files
set tracefile [open "tcp_vs_udp_comparison.tr" w]
$ns trace-all $tracefile

set namfile [open "tcp_vs_udp_comparison.nam" w]
$ns namtrace-all $namfile

# Open CWND trace file to monitor TCP Congestion Window evolution
set cwndfile [open "tcp_cwnd.tr" w]

# Procedure to record TCP congestion window (cwnd) every 10ms
proc record_cwnd {} {
    global ns tcp0 cwndfile
    set time 0.01
    set now [$ns now]
    set cwnd [$tcp0 set cwnd_]
    puts $cwndfile "$now $cwnd"
    $ns at [expr $now + $time] "record_cwnd"
}

# Finish procedure
proc finish {} {
    global ns tracefile namfile cwndfile
    $ns flush-trace
    close $tracefile
    close $namfile
    close $cwndfile
    puts "=========================================================="
    puts " TCP vs UDP Simulation Finished Successfully!"
    puts " Output trace generated : tcp_vs_udp_comparison.tr"
    puts " Output NAM generated   : tcp_vs_udp_comparison.nam"
    puts " TCP CWND trace         : tcp_cwnd.tr"
    puts "=========================================================="
    exit 0
}

# ==============================================================================
# Topology Setup: Sources, Bottleneck Router, and Central Destination
# ==============================================================================
# Node 0: Smart City IoT / CCTV Source (UDP)
# Node 1: Smart City Traffic Management Control Node (TCP)
# Node 2: Intermediate Core Router
# Node 3: Central Gateway / Bottleneck Router
# Node 4: Central Server Destination (TMC Cloud)

set n0 [$ns node]  ;# UDP Source (CCTV)
set n1 [$ns node]  ;# TCP Source (TMC Control / Critical Signals)
set n2 [$ns node]  ;# Core Router
set n3 [$ns node]  ;# Bottleneck Gateway Router
set n4 [$ns node]  ;# Central TMC Server

$n0 label "UDP_Source_CCTV"
$n1 label "TCP_Source_TMC_Control"
$n2 label "Core_Router"
$n3 label "Bottleneck_Gateway"
$n4 label "Central_Destination"

$n0 shape circle; $n0 color red
$n1 shape box;    $n1 color blue
$n2 shape square; $n2 color black
$n3 shape square; $n3 color brown
$n4 shape box;    $n4 color navy

# Access Links (High capacity, low delay)
$ns duplex-link $n0 $n2 10Mb 2ms DropTail
$ns duplex-link $n1 $n2 10Mb 2ms DropTail

# Intermediate Distribution Link
$ns duplex-link $n2 $n3 10Mb 5ms DropTail

# Bottleneck Link (2.0 Mbps capacity, 20ms delay, Queue buffer limit = 15 packets)
# Both TCP and UDP flows must share this constrained channel
$ns duplex-link $n3 $n4 2.0Mb 20ms DropTail
$ns queue-limit $n3 $n4 15

# Visual Link Orientations
$ns duplex-link-op $n0 $n2 orient right-down
$ns duplex-link-op $n1 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right
$ns duplex-link-op $n3 $n4 queuePos 0.5

# ==============================================================================
# Flow 1: UDP / CBR Flow (Unthrottled, High-rate Video Feed)
# ==============================================================================
set udp0 [new Agent/UDP]
$udp0 set class_ 1
$udp0 set fid_ 1
$ns attach-agent $n0 $udp0

set null0 [new Agent/Null]
$ns attach-agent $n4 $null0
$ns connect $udp0 $null0

set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 1024
$cbr0 set rate_ 2.5Mb
$cbr0 set random_ 0
$cbr0 attach-agent $udp0

# ==============================================================================
# Flow 2: TCP Flow (Reliable Transmission with Congestion Control - NewReno)
# ==============================================================================
set tcp0 [new Agent/TCP/Newreno]
$tcp0 set class_ 2
$tcp0 set fid_ 2
$tcp0 set window_ 32
$tcp0 set packetSize_ 1024
$ns attach-agent $n1 $tcp0

set sink0 [new Agent/TCPSink]
$ns attach-agent $n4 $sink0
$ns connect $tcp0 $sink0

set ftp0 [new Application/FTP]
$ftp0 attach-agent $tcp0

# ==============================================================================
# Simulation Event Scheduling
# ==============================================================================
# TCP transmission starts first to establish connection and ramp up cwnd
$ns at 0.5 "$ftp0 start"

# Start monitoring TCP CWND
$ns at 0.5 "record_cwnd"

# UDP (unregulated burst) enters the network at t=2.0s, creating sudden congestion
$ns at 2.0 "$cbr0 start"

# UDP stops at t=6.5s, allowing TCP to recover and regain bandwidth
$ns at 6.5 "$cbr0 stop"

# TCP transmission completes
$ns at 9.0 "$ftp0 stop"

# Finish simulation
$ns at 10.0 "finish"

# Execute
$ns run
