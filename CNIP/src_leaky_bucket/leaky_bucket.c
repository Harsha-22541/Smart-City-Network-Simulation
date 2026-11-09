/*
 * ==============================================================================
 * Leaky Bucket Traffic Shaper Algorithm
 * Subject : Computer Networks / Smart City Traffic Control
 * Description: Implements the classic Leaky Bucket algorithm for traffic shaping
 *              and congestion avoidance. Simulates a finite queue buffer (bucket)
 *              receiving bursty incoming packets and leaking them at a constant
 *              rate, preventing downstream buffer overflow.
 * Language: C (Standard C99)
 * ==============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_TIME_STEPS 10

typedef struct {
    int bucket_capacity;    // Maximum capacity of the buffer (in packets/bytes)
    int leak_rate;          // Constant outgoing transmission rate (units per second)
    int current_occupancy;  // Current amount stored in buffer
    int total_received;     // Total units arriving
    int total_transmitted;  // Total units successfully leaked
    int total_dropped;      // Total units dropped due to overflow
} LeakyBucket;

// Function to initialize the leaky bucket
void init_leaky_bucket(LeakyBucket* lb, int capacity, int leak_rate) {
    lb->bucket_capacity = capacity;
    lb->leak_rate = leak_rate;
    lb->current_occupancy = 0;
    lb->total_received = 0;
    lb->total_transmitted = 0;
    lb->total_dropped = 0;
}

// Function to process arriving traffic at a single time step
void process_packet(LeakyBucket* lb, int time_sec, int incoming_packets) {
    lb->total_received += incoming_packets;
    int accepted = 0;
    int dropped = 0;
    int transmitted = 0;

    // Check buffer availability
    int free_space = lb->bucket_capacity - lb->current_occupancy;
    if (incoming_packets <= free_space) {
        accepted = incoming_packets;
        lb->current_occupancy += incoming_packets;
    } else {
        accepted = free_space;
        dropped = incoming_packets - free_space;
        lb->current_occupancy = lb->bucket_capacity;
        lb->total_dropped += dropped;
    }

    // Leak packets out at constant rate
    if (lb->current_occupancy >= lb->leak_rate) {
        transmitted = lb->leak_rate;
        lb->current_occupancy -= lb->leak_rate;
    } else {
        transmitted = lb->current_occupancy;
        lb->current_occupancy = 0;
    }
    lb->total_transmitted += transmitted;

    // Display row in simulation table
    printf("%-5d | %-9d | %-8d | %-7d | %-11d | %-10d | %6.2f%%\n",
           time_sec,
           incoming_packets,
           accepted,
           dropped,
           transmitted,
           lb->current_occupancy,
           ((double)lb->current_occupancy / lb->bucket_capacity) * 100.0);
}

int main() {
    int capacity = 15;   // Bucket buffer capacity = 15 packets
    int leak_rate = 4;    // Constant leak rate = 4 packets/sec

    // Simulated Smart City incoming bursty traffic at each second (IoT + CCTV bursts)
    int bursty_traffic[MAX_TIME_STEPS] = {3, 8, 12, 14, 5, 2, 16, 4, 1, 0};

    LeakyBucket lb;
    init_leaky_bucket(&lb, capacity, leak_rate);

    printf("========================================================================================\n");
    printf("                  SMART CITY LEAKY BUCKET CONGESTION MANAGEMENT SIMULATION              \n");
    printf("========================================================================================\n");
    printf(" Parameters: Bucket Buffer Capacity = %d packets | Constant Leak Rate = %d packets/sec\n",
           capacity, leak_rate);
    printf("----------------------------------------------------------------------------------------\n");
    printf("Time  | Incoming  | Accepted | Dropped | Transmitted | Buffer Rem | Buffer Util\n");
    printf("(sec) | (Packets) | (Buffer) | (Drops) | (Leaked)    | (Packets)  | (%%)\n");
    printf("------+-----------+----------+---------+-------------+------------+-------------\n");

    for (int t = 0; t < MAX_TIME_STEPS; t++) {
        process_packet(&lb, t + 1, bursty_traffic[t]);
    }

    // Drain remaining packets in buffer if any
    int extra_time = MAX_TIME_STEPS + 1;
    while (lb.current_occupancy > 0) {
        process_packet(&lb, extra_time++, 0);
    }

    printf("========================================================================================\n");
    printf("                               SIMULATION SUMMARY RESULTS                               \n");
    printf("========================================================================================\n");
    printf(" Total Packets Received       : %d\n", lb.total_received);
    printf(" Total Packets Transmitted    : %d (%.2f%% throughput efficiency)\n",
           lb.total_transmitted, ((double)lb.total_transmitted / lb.total_received) * 100.0);
    printf(" Total Packets Dropped        : %d (%.2f%% drop rate)\n",
           lb.total_dropped, ((double)lb.total_dropped / lb.total_received) * 100.0);
    printf(" Final Buffer Occupancy       : %d packets\n", lb.current_occupancy);
    printf("========================================================================================\n");

    return 0;
}
