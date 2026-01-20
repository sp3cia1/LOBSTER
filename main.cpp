#include <cstdint>
#include <string>
#include <sstream>
#include <iostream>
#include "Order.h"
#include "OrderBook.h"
#include "OrderHandler.h"

using namespace std;

int main(){
    string command;
    OrderBook orderBook;
    while(true){
        cout << "Enter Command(B/S/C) Quantity/OrderId(for C) Price" << endl;
        if (!getline(cin, command)) break;
        if (command.empty()) continue;
        handleClientCommand(orderBook, command, -1);
    }
}