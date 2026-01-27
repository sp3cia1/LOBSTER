#include <iostream>
#include <vector>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netinet/tcp.h>
#include <cstring>

int createAndConnectSocket() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("socket");
        return -1;
    }

    int flag = 1;
    if (setsockopt(sock, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(int)) < 0) {
        perror("setsockopt TCP_NODELAY");
        close(sock);
        return -1;
    }

    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(54321);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);

    if (connect(sock, reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) == -1) {
        perror("connect");
        close(sock);
        return -1;
    }

    return sock;
}

double pingPong(int sock) {
    const char* message = "B 100 10\n";
    char buffer[256];

    auto start = std::chrono::steady_clock::now();
    
    ssize_t sent = send(sock, message, strlen(message), 0);
    if (sent <= 0) {
        std::cerr << "send failed\n";
        return -1.0;
    }

    // wait
    ssize_t received = recv(sock, buffer, sizeof(buffer), 0);
    if (received <= 0) {
        std::cerr << "recv failed\n";
        return -1.0;
    }

    auto end = std::chrono::steady_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    return static_cast<double>(duration);
}

int main() {
    std::cout << "Connecting to server at 127.0.0.1:54321...\n";
    
    int sock = createAndConnectSocket();
    if (sock == -1) {
        std::cerr << "Failed to connect to server\n";
        return 1;
    }

    std::cout << "Connected. TCP_NODELAY enabled.\n\n";

    std::cout << "Running warmup (1,000 iterations)...\n";
    for (int i = 0; i < 1000; ++i) {
        double latency = pingPong(sock);
        if (latency < 0) {
            std::cerr << "Warmup failed at iteration " << i << "\n";
            close(sock);
            return 1;
        }
    }
    std::cout << "Warmup complete.\n\n";

    std::cout << "Running benchmark (10,000 iterations)...\n";
    std::vector<double> latencies;
    latencies.reserve(10000);

    for (int i = 0; i < 10000; ++i) {
        double latency = pingPong(sock);
        if (latency < 0) {
            std::cerr << "Benchmark failed at iteration " << i << "\n";
            close(sock);
            return 1;
        }
        latencies.push_back(latency);
    }
    std::cout << "Benchmark complete.\n\n";

    // sort for percentile calculations
    std::sort(latencies.begin(), latencies.end());

    double minLatency = latencies.front();
    double avgLatency = std::accumulate(latencies.begin(), latencies.end(), 0.0) / latencies.size();
    double p99Latency = latencies[9900]; // 99th percentile at index 9,900

    std::cout << "=== Benchmark Results ===\n";
    std::cout << "Min Latency: " << minLatency << " μs\n";
    std::cout << "Avg Latency: " << avgLatency << " μs\n";
    std::cout << "P99 Latency: " << p99Latency << " μs\n";

    close(sock);
    return 0;
}
