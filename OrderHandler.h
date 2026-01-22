#pragma once
#include <string>
#include <cstdint>
#include <sstream>
#include <optional>
#include <sys/socket.h>
#include <cstring>
#include "OrderBook.h"

std::uint64_t getNextId()
{
    static std::uint64_t id = 0;
    return ++id;
};

void sendMessage(std::string message, int socket)
{
    if (socket != -1)
    {
        send(socket, message.c_str(), message.length(), 0);
    }
    std::cout << message << std::endl;
}

void handleClientCommand(OrderBook &book, std::string command, int clientSocket)
{
    std::string message;
    std::stringstream ss(command);
    std::string type;
    std::uint32_t quantity = 0;
    std::uint32_t price = 0;
    ss >> type;
    if (type == "B" || type == "S")
    {
        ss >> quantity;
        ss >> price;
        if (quantity > 0 && price > 0)
        {
            Side side = type == "B" ? Side::Buy : Side::Sell;
            std::uint64_t id = getNextId();
            Order order;
            order.orderId = id;
            order.price = price;
            order.quantity = quantity;
            order.side = side;
            book.addOrder(order);
            message = "Order " + std::to_string(id) + " placed.\n";            
            sendMessage(message, clientSocket);
            book.match();
        }
        else
        {
            sendMessage("Invalid Order", clientSocket);
            return;
        }
    }
    else if (type == "C")
    {
        std::uint64_t orderId;
        ss >> orderId;
        if (orderId > 0)
        {
            book.cancelOrder(orderId);
            message = "Order " + std::to_string(orderId) + " canceled.\n";            
            sendMessage(message, clientSocket);
        }
        else
        {
            sendMessage("Invalid Order", clientSocket);
            return;
        }
    }
    else
    {
        sendMessage("Invalid Order", clientSocket);
        return;
    }
}