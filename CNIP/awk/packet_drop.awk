# ==============================================================================
# AWK Script: packet_drop.awk
# Description: Analyzes dropped packets, identifying dropped node locations,
#              packet drop count by flow ID, and overall drop ratio.
# Usage:
#   awk -f packet_drop.awk smart_city_baseline.tr
# ==============================================================================

BEGIN {
    total_sent = 0;
    total_dropped = 0;
    total_received = 0;
}

{
    event = $1;
    time = $2;
    fromNode = $3;
    toNode = $4;
    pktType = $5;
    pktSize = $6;
    flowId = $8;
    destAddr = $10;

    # Count packet transmissions (+ at source nodes)
    if (event == "+") {
        total_sent++;
        flow_sent[flowId]++;
    }

    # Count packet arrivals at destination
    if (event == "r") {
        total_received++;
        flow_recv[flowId]++;
    }

    # Count packet drop events
    if (event == "d") {
        total_dropped++;
        flow_dropped[flowId]++;
        node_drops[fromNode]++;
        drop_reason[fromNode, toNode]++;
    }
}

END {
    print "======================================================";
    print "               PACKET DROP ANALYSIS REPORT            ";
    print "======================================================";
    printf " Total Packets Enqueued  : %d\n", total_sent;
    printf " Total Packets Received  : %d\n", total_received;
    printf " Total Packets Dropped   : %d\n", total_dropped;
    
    if (total_sent > 0) {
        drop_rate = (total_dropped / total_sent) * 100;
        printf " Packet Drop Ratio (PDR) : %.2f %%\n", drop_rate;
    }
    
    print "------------------------------------------------------";
    print " Packet Drops by Flow ID (Traffic Category):";
    print "------------------------------------------------------";
    print " Flow ID | Category               | Sent  | Dropped | Drop %";
    print "---------+------------------------+-------+---------+--------";
    for (fid in flow_sent) {
        name = "Unknown";
        if (fid == 1) name = "Traffic Signal";
        if (fid == 2) name = "CCTV Video Stream";
        if (fid == 3) name = "Pollution Sensor";
        if (fid == 4) name = "Smart Lighting";
        if (fid == 5) name = "Emergency Service";
        
        sent = flow_sent[fid];
        drop = (flow_dropped[fid] == "") ? 0 : flow_dropped[fid];
        pct = (sent > 0) ? (drop / sent) * 100 : 0;
        
        printf " %-7d | %-22s | %-5d | %-7d | %6.2f %%\n", fid, name, sent, drop, pct;
    }
    
    print "------------------------------------------------------";
    print " Packet Drops by Node Link (Buffer Overflow Locations):";
    print "------------------------------------------------------";
    for (node in node_drops) {
        printf " Router Node %s dropped %d packets due to buffer overflow\n", node, node_drops[node];
    }
    print "======================================================";
}
