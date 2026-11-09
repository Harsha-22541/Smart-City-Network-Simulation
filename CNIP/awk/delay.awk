# ==============================================================================
# AWK Script: delay.awk
# Description: Calculates average end-to-end packet transmission delay:
#              Delay = Receive Time (at dest) - Send Time (at source)
# Usage:
#   awk -f delay.awk smart_city_baseline.tr
# ==============================================================================

BEGIN {
    total_delay = 0;
    count = 0;
    min_delay = 1e9;
    max_delay = 0;
}

{
    event = $1;
    time = $2;
    fromNode = $3;
    toNode = $4;
    pktType = $5;
    pktId = $12;

    # Record sending time when packet is enqueued at source
    if (event == "+" && (fromNode < 7)) {
        start_time[pktId] = time;
    }

    # Record arrival time when packet is received at destination (Node 10)
    if (event == "r" && toNode == 10) {
        if (start_time[pktId] > 0) {
            end_time = time;
            pkt_delay = end_time - start_time[pktId];

            total_delay += pkt_delay;
            count++;

            if (pkt_delay < min_delay) min_delay = pkt_delay;
            if (pkt_delay > max_delay) max_delay = pkt_delay;
        }
    }
}

END {
    print "======================================================";
    print "            END-TO-END DELAY ANALYSIS REPORT          ";
    print "======================================================";
    printf " Total Delivered Packets Measured : %d\n", count;
    
    if (count > 0) {
        avg_delay = (total_delay / count) * 1000; # in milliseconds
        printf " Minimum End-to-End Delay        : %.3f ms\n", (min_delay * 1000);
        printf " Maximum End-to-End Delay        : %.3f ms\n", (max_delay * 1000);
        printf " Average End-to-End Delay        : %.3f ms\n", avg_delay;
    } else {
        print " No packet round-trip events found in trace file.";
    }
    print "======================================================";
}
