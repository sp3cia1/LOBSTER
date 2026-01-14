#include <iostream>
#include <array>
#include <string>
#include <stdexcept>
using namespace std;

enum OrderType
{
    Buy,
    Sell
};

struct Order
{
    OrderType orderType;
    int quantity;
    int price;
    bool error;
    string errorMessage;
    

    Order(array<string, 3> orderInput)
    {
        error = false;
        errorMessage = "";

        if (orderInput[0] == "Buy")
        {
            orderType = Buy;
        }
        else if (orderInput[0] == "Sell")
        {
            orderType = Sell;
        }
        else
        {
            error = true;
            errorMessage = "Only \"Buy\" and \"Sell\" orders allowed.";
            return;
        }

        if (stoi(orderInput[1]) > 0)
        {
            quantity = stoi(orderInput[1]);
        }
        else
        {
            error = true;
            errorMessage = "Please give a quantity greater then 0.";
            return;
        }

        if (stoi(orderInput[2]) > 0)
        {
            price = stoi(orderInput[2]);
        }
        else
        {
            error = true;
            errorMessage = "Please give a price greater then 0.";
            return;
        }
    }
};

int main()
{
    cout << "Buy or Sell" << endl;
    array<string, 3> orderInput;
    for (int i = 0; i < 3; i++)
    {
        cin >> orderInput[i];
    }
    Order order(orderInput);
    if (order.error) {
        cout << "Error: " << order.errorMessage << endl;
    } else {
        cout << "Success!" << endl;
    }
}