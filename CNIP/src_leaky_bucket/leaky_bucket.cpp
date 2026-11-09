/*
 * ==============================================================================
 * Leaky Bucket Algorithm (C++ OOP Implementation)
 * Project: Smart City Network Simulation and Congestion Analysis
 * Description: Object-oriented C++ implementation of Leaky Bucket traffic
 *              shaper with queue occupancy tracking, overflow drop logging,
 *              and throughput metrics calculation.
 * ==============================================================================
 */

#include <iostream>
#include <vector>
#include <iomanip>

class LeakyBucket {
private:
    int capacity;
    int leakRate;
    int currentBuffer;
    int totalReceived;
    int totalTransmitted;
    int totalDropped;

public:
    LeakyBucket(int cap, int rate) 
        : capacity(cap), leakRate(rate), currentBuffer(0),
          totalReceived(0), totalTransmitted(0), totalDropped(0) {}

    void process(int timeSec, int incoming) {
        totalReceived += incoming;
        int space = capacity - currentBuffer;
        int accepted = 0;
        int dropped = 0;
        int transmitted = 0;

        if (incoming <= space) {
            accepted = incoming;
            currentBuffer += incoming;
        } else {
            accepted = space;
            dropped = incoming - space;
            currentBuffer = capacity;
            totalDropped += dropped;
        }

        if (currentBuffer >= leakRate) {
            transmitted = leakRate;
            currentBuffer -= leakRate;
        } else {
            transmitted = currentBuffer;
            currentBuffer = 0;
        }
        totalTransmitted += transmitted;

        double util = (static_cast<double>(currentBuffer) / capacity) * 100.0;
        std::cout << std::setw(5) << timeSec << " | "
                  << std::setw(9) << incoming << " | "
                  << std::setw(8) << accepted << " | "
                  << std::setw(7) << dropped << " | "
                  << std::setw(11) << transmitted << " | "
                  << std::setw(10) << currentBuffer << " | "
                  << std::setw(7) << std::fixed << std::setprecision(2) << util << "%\n";
    }

    bool hasResidual() const {
        return currentBuffer > 0;
    }

    void printSummary() const {
        std::cout << "========================================================================================\n";
        std::cout << "                               SIMULATION SUMMARY REPORT                                \n";
        std::cout << "========================================================================================\n";
        std::cout << " Total Arrived Packets     : " << totalReceived << "\n";
        std::cout << " Total Transmitted Packets : " << totalTransmitted << " (" 
                  << (static_cast<double>(totalTransmitted) / totalReceived * 100.0) << "%)\n";
        std::cout << " Total Packets Dropped     : " << totalDropped << " (" 
                  << (static_cast<double>(totalDropped) / totalReceived * 100.0) << "%)\n";
        std::cout << " Final Buffer Residual     : " << currentBuffer << " packets\n";
        std::cout << "========================================================================================\n";
    }
};

int main() {
    int cap = 15;
    int rate = 4;
    std::vector<int> traffic = {3, 8, 12, 14, 5, 2, 16, 4, 1, 0};

    LeakyBucket lb(cap, rate);

    std::cout << "========================================================================================\n";
    std::cout << "                 SMART CITY TRAFFIC SHAPING: LEAKY BUCKET (C++ OOP)                     \n";
    std::cout << "========================================================================================\n";
    std::cout << " Buffer Capacity = " << cap << " pkts | Constant Outflow Rate = " << rate << " pkts/sec\n";
    std::cout << "----------------------------------------------------------------------------------------\n";
    std::cout << "Time  | Incoming  | Accepted | Dropped | Transmitted | Buffer Rem | Buffer Util\n";
    std::cout << "(sec) | (Packets) | (Buffer) | (Drops) | (Leaked)    | (Packets)  | (%)\n";
    std::cout << "------+-----------+----------+---------+-------------+------------+-------------\n";

    int t = 1;
    for (int inc : traffic) {
        lb.process(t++, inc);
    }
    while (lb.hasResidual()) {
        lb.process(t++, 0);
    }

    lb.printSummary();
    return 0;
}
