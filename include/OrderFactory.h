#pragma once
#include <vector>
#include <random>
#include "Order.h"

class OrderFactory
{
public:
    static std::vector<Order> generateOrder(int count)
    {
        std::vector<Order> orders;
        orders.reserve(count);

        std::mt19937 gen(42);
        std::uniform_int_distribution<uint32_t> priceDist(80, 120);
        // using a tight spread between 80 dollars and 120 dollars to generate more orders that match and stres test the system
        std::uniform_int_distribution<uint32_t> qtyDist(1, 100);
        for (int i = 0; i < count; i++)
        {
            Order order;
            order.side = i % 2 == 0 ? Side::Buy : Side::Sell;
            order.orderId = i + 1;
            order.price = priceDist(gen);
            order.quantity = qtyDist(gen);
            orders.push_back(order);
        }
        return orders;
    }
};