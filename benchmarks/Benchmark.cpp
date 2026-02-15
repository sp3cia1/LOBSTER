#include <iostream>
#include <chrono>
#include "OrderBook.h"
#include "OrderFactory.h"

int main()
{
    std::cout << "Generating orders...\n";
    auto mainOrders = OrderFactory::generateOrder(1000000);
    auto warmupOrders = OrderFactory::generateOrder(10000);
    std::cout << "Generated " << mainOrders.size() << " main orders and " 
              << warmupOrders.size() << " warmup orders.\n\n";

    // warmup phase (untimed)
    std::cout << "Warming up...\n";
    {
        OrderBook warmupBook;
        for (const auto& order : warmupOrders) {
            warmupBook.addOrder(order);
        }
    } 
    std::cout << "Warmup complete.\n\n";

    // timed
    std::cout << "Starting benchmark...\n";
    OrderBook realBook;
    
    auto start = std::chrono::steady_clock::now();
    for (const auto& order : mainOrders) {
        realBook.addOrder(order);
    }
    auto end = std::chrono::steady_clock::now();

    auto durationMicros = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    auto durationSeconds = durationMicros / 1000000.0;
    
    double latencyMicros = static_cast<double>(durationMicros) / 1000000.0;
    double throughput = 1000000.0 / durationSeconds;

    std::cout << "\n=== Benchmark Results ===\n";
    std::cout << "Total Duration: " << durationMicros << " μs (" << durationSeconds << " s)\n";
    std::cout << "Average Latency: " << latencyMicros << " μs per order\n";
    std::cout << "Throughput: " << throughput << " orders/second\n";

    return 0;
}
