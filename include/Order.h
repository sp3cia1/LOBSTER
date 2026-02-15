#pragma once
#include <cstdint>

enum class Side {
    Buy, Sell
};

struct Order {
    uint64_t orderId;
    uint32_t price;
    uint32_t quantity;
    Side side;
};