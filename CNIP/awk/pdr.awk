# ==============================================================================
# AWK Script: pdr.awk
# Description: Calculates Packet Delivery Ratio (PDR) for the simulation:
#              PDR = (Total Packets Received / Total Packets Sent) * 100%
# Usage:
#   awk -f pdr.awk smart_city_baseline.tr
# ==============================================================================

BEGIN {
    send_packets = 0;
    recv_packets = 0;
}

{
    event = $1;
    fromNode = $3;
    toNode = $4;
    pktType = $5;
    flowId = $8;

    # Enqueue at edge source nodes
    if (event == "+" && (fromNode == 0 || fromNode == 1 || fromNode == 2 || fromNode == 3 || fromNode == 4 || fromNode == 5 || fromNode == 6)) {
        send_packets++;
    }

    # Packet received at destination node (Node 10)
    if (event == "r" && toNode == 10) {
        recv_packets++;
    }
}

END {
    print "======================================================";
    print "           PACKET DELIVERY RATIO (PDR) ANALYSIS       ";
    print "======================================================";
    printf " Total Packets Generated (Sent)  : %d\n", send_packets;
    printf " Total Packets Delivered (Recv)  : %d\n", recv_packets;
    
    if (send_packets > 0) {
        pdr = (recv_packets / send_packets) * 100;
        printf " Packet Delivery Ratio (PDR)     : %.2f %%\n", pdr;
    } else {
        print " No packets were sent during the simulation.";
    }
    print "======================================================";
}
