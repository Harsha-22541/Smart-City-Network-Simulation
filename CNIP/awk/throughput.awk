# ==============================================================================
# AWK Script: throughput.awk
# Description: Calculates average throughput and periodic instantaneous
#              throughput from an NS-2 trace file (.tr).
# Usage:
#   awk -f throughput.awk smart_city_baseline.tr
#   awk -v dest=10 -v time_interval=0.5 -f throughput.awk smart_city_baseline.tr
# ==============================================================================

BEGIN {
    recvdSize = 0;
    startTime = 1e9;
    stopTime = 0;
    
    # Defaults if not supplied via -v
    if (dest == "") dest = 10;
    if (time_interval == "") time_interval = 0.5;
    
    current_window = time_interval;
    window_bytes = 0;
    
    print "------------------------------------------------------";
    print " Time (s)   | Interval Throughput (Kbps)";
    print "------------------------------------------------------";
}

{
    event = $1;
    time = $2;
    fromNode = $3;
    toNode = $4;
    pktType = $5;
    pktSize = $6;
    flowId = $8;

    # Look for receive events at the destination node
    if (event == "r" && toNode == dest) {
        if (time < startTime) {
            startTime = time;
        }
        if (time > stopTime) {
            stopTime = time;
        }

        recvdSize += pktSize;
        window_bytes += pktSize;

        # Print periodic throughput windows
        if (time >= current_window) {
            thr_interval = (window_bytes * 8) / (time_interval * 1000); # in Kbps
            printf " %8.2f   | %12.2f Kbps\n", current_window, thr_interval;
            window_bytes = 0;
            current_window += time_interval;
        }
    }
}

END {
    duration = stopTime - startTime;
    if (duration > 0) {
        total_bits = recvdSize * 8;
        throughput_kbps = (total_bits / duration) / 1000;
        throughput_mbps = throughput_kbps / 1000;
        
        print "======================================================";
        print "               OVERALL THROUGHPUT SUMMARY            ";
        print "======================================================";
        printf " Destination Node         : %s\n", dest;
        printf " Transmission Start Time : %.4f sec\n", startTime;
        printf " Transmission Stop Time  : %.4f sec\n", stopTime;
        printf " Total Active Duration   : %.4f sec\n", duration;
        printf " Total Data Received     : %.2f KB (%.2f MB)\n", (recvdSize / 1024), (recvdSize / (1024 * 1024));
        printf " Average Throughput      : %.2f Kbps (%.4f Mbps)\n", throughput_kbps, throughput_mbps;
        print "======================================================";
    } else {
        print "No packets received at destination node " dest;
    }
}
