# ==============================================================================
# AWK Script: buffer_utilization.awk
# Description: Analyzes queue occupancy and buffer utilization at the bottleneck
#              gateway link (Node 9 -> Node 10).
# Usage:
#   awk -f buffer_utilization.awk smart_city_baseline.tr
# ==============================================================================

BEGIN {
    curr_q = 0;
    max_q = 0;
    total_q_samples = 0;
    sum_q = 0;
    buffer_drops = 0;
    last_time = 0;
}

{
    event = $1;
    time = $2;
    fromNode = $3;
    toNode = $4;
    pktSize = $6;

    # Trace queue operations on the bottleneck link (9 -> 10)
    if (fromNode == 9 && toNode == 10) {
        if (event == "+") {
            curr_q++;
            if (curr_q > max_q) max_q = curr_q;
        } else if (event == "-") {
            if (curr_q > 0) curr_q--;
        } else if (event == "d") {
            buffer_drops++;
        }

        sum_q += curr_q;
        total_q_samples++;
    }
}

END {
    print "======================================================";
    print "        BOTTLENECK BUFFER UTILIZATION REPORT          ";
    print "======================================================";
    printf " Monitored Bottleneck Link      : Node 9 -> Node 10\n";
    printf " Peak Queue Occupancy           : %d packets\n", max_q;
    if (total_q_samples > 0) {
        avg_q = sum_q / total_q_samples;
        printf " Average Queue Occupancy        : %.2f packets\n", avg_q;
    }
    printf " Buffer Overflow Drops          : %d packets\n", buffer_drops;
    print "======================================================";
}
