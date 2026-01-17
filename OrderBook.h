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
        if (OrderPtrs.find(order.orderId) != OrderPtrs.end()){
            return;
        }
        if (order.side == Side::Buy){
            auto it = bids[order.price].insert(bids[order.price].end(), order);
            OrderPtrs[order.orderId] = it;
        } else if (order.side == Side::Sell){
            auto it = asks[order.price].insert(asks[order.price].end(), order);
            OrderPtrs[order.orderId] = it;
        } else {
            return;
        }
    }
    void cancelOrder(std::uint64_t orderId){
        if (!OrderPtrs.count(orderId) == 0){
            return;
        }
        auto it = OrderPtrs[orderId];
        if (it->side == Side::Buy){
            bids[it->price].erase(it);
            if (bids[it->price].empty()){
                bids.erase(it->price);
            }
        } else{
            asks[it->price].erase(it);
            if (asks[it->price].empty()){
                asks.erase(it->price);
            }
        }
        OrderPtrs.erase(orderId);
    };
    void match(){

    };
};