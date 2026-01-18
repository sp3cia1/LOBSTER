#include <cstdint>
#include <string>
#include <sstream>
#include <iostream>
#include "Order.h"
#include "OrderBook.h"

using namespace std;

uint64_t getNextId() { 
    static uint64_t id = 0; 
    return ++id; 
};

int main(){
    string command;
    OrderBook orderBook;
    while(true){
        cout << "Enter Command(B/S/C) Quantity/OrderId(for C) Price";
        if (!getline(cin, command)) break;
        if (command.empty()) continue;
        stringstream ss(command);
        string type;
        uint32_t quantity = 0;
        uint32_t price = 0;
        ss >> type;
        if (type == "B" || type == "S"){
            ss >> quantity;
            ss >> price;
            if (quantity > 0 && price > 0){
                Side side = type == "B" ? Side::Buy : Side::Sell;
                uint64_t id = getNextId();
                Order order;
                order.orderId = id;
                order.price = price;
                order.quantity = quantity;
                order.side = side;
                orderBook.addOrder(order);
                cout << "Order " << id << " placed."<<endl;
                orderBook.match();
            } else{
                cout << "Invalid Order" << endl;
                continue;
            }
        } else if (type == "C"){
            uint64_t orderId;
            ss >> orderId;
            if (orderId > 0){
                orderBook.cancelOrder(orderId);
                cout << "Order " << orderId << " canceled."<<endl;
            } else{
                cout << "Invalid Order" << endl;
                continue;
            }
        } else{
            cout << "Invalid Order" << endl;
            continue;
        }
    }
}