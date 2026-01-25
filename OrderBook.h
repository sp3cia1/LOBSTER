#pragma once
#include <iostream>
#include <list>
#include <map>
#include <unordered_map>
#include <cstdint>
#include <mutex>
#include <functional>
#include "Order.h"

class OrderBook {

public:
    std::function<void(uint32_t, uint32_t)> onTrade;

    void addOrder(Order order){
        std::lock_guard<std::mutex> guard(bookMutex);
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
        std::lock_guard<std::mutex> guard(bookMutex);
        if (OrderPtrs.count(orderId) == 0){
            return;
        }
        auto it = OrderPtrs[orderId];
        // not using & as It is a small "pointer". Copying is safer. prevents dangling ref after erase
        if (it->side == Side::Buy){
            deleteBidOrder(it->price, it->orderId);
        } else{
            deleteAskOrder(it->price, it->orderId);
        }
    };
    void match(){
        std::lock_guard<std::mutex> guard(bookMutex);
        while(!bids.empty() && !asks.empty()){
            auto& [bestBidPrice, bestBidList] = *bids.begin();
            auto& [bestAskPrice, bestAskList] = *asks.begin();
            // copying the list on every loop is expensive so we used & here to refrence it in memory instead.
            if (bestBidPrice < bestAskPrice){
                return;
            }
            Order& bidOrder = bestBidList.front();
            Order& askOrder = bestAskList.front();
            std::uint32_t bidPrice = bidOrder.price;
            std::uint32_t askPrice = askOrder.price;
            std::uint64_t bidId = bidOrder.orderId;
            std::uint64_t askId = askOrder.orderId;
            uint32_t quantity = std::min(bidOrder.quantity, askOrder.quantity);
            if (onTrade) {
                onTrade(askOrder.price, quantity);
            }
            //we use ask price assuming the sell order was the maker in our simplified model
            bidOrder.quantity -= quantity;
            askOrder.quantity -= quantity;
            if (bidOrder.quantity == 0){
                deleteBidOrder(bidPrice, bidId);
            }
            if (askOrder.quantity == 0){
                deleteAskOrder(askPrice, askId);
            }
            // after this delete call, 'bestBidList' might become a dangling reference if the list was empty and removed from the map.We do NOT use 'bestBidList' or 'bidOrder' again in this loop iteration.
        }
    };

private:    
    std::map<std::uint32_t, std::list<Order>, std::greater<std::uint32_t>> bids;
    std::map<std::uint32_t, std::list<Order>, std::less<std::uint32_t>> asks;
    std::unordered_map<std::uint64_t, std::list<Order>::iterator> OrderPtrs;
    mutable std::mutex bookMutex;

    void deleteBidOrder(std::uint32_t price, std::uint64_t orderId) {
        auto it = bids.find(price);
        if (it != bids.end()) {
            it->second.erase(OrderPtrs[orderId]);
            if (it->second.empty()) {
                bids.erase(it); 
            }
        }
        OrderPtrs.erase(orderId);
    }

    void deleteAskOrder(std::uint32_t price, std::uint64_t orderId) {
        auto it = asks.find(price);
        if (it != asks.end()) {
            it->second.erase(OrderPtrs[orderId]);
            if (it->second.empty()) {
                asks.erase(it);
            }
        }
        OrderPtrs.erase(orderId);
    }
};