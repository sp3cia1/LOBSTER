#include <list>
#include <map>
#include <unordered_map>
#include "Order.h"
#include <cstdint>

class OrderBook {
    std::map<std::uint32_t, std::list<Order>, std::greater<std::uint32_t>> bids;
    std::map<std::uint32_t, std::list<Order>, std::less<std::uint32_t>> asks;
    std::unordered_map<std::uint64_t, std::list<Order>::iterator> OrderPtrs;

public:
    void addOrder(Order order){

    };
    void cancelOrder(std::uint64_t orderId){

    };
    void match(){

    };
};