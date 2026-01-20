#pragma once
#include <string>
#include <cstdint>
#include <sstream>
#include <optional>
#include <sys/socket.h>
#include <cstring>
#include "OrderBook.h"

using namespace std;

uint64_t getNextId()
{
    static uint64_t id = 0;
    return ++id;
};

void sendMessage(string message, int socket)
{
    if (socket != -1)
    {
        send(socket, message.c_str(), message.length(), 0);
    }
    cout << message << endl;
}

void handleClientCommand(OrderBook &book, string command, int clientSocket)
{
    string message;
    stringstream ss(command);
    string type;
    uint32_t quantity = 0;
    uint32_t price = 0;
    ss >> type;
    if (type == "B" || type == "S")
    {
        ss >> quantity;
        ss >> price;
        if (quantity > 0 && price > 0)
        {
            Side side = type == "B" ? Side::Buy : Side::Sell;
            uint64_t id = getNextId();
            Order order;
            order.orderId = id;
            order.price = price;
            order.quantity = quantity;
            order.side = side;
            book.addOrder(order);
            message = "Order " + to_string(id) + " placed.\n";            
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
        uint64_t orderId;
        ss >> orderId;
        if (orderId > 0)
        {
            book.cancelOrder(orderId);
            message = "Order " + to_string(orderId) + " canceled.\n";            
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