
#include <iostream>

#include "intersection.h"

int main()
{
    const std::vector<std::pair<int, int>> points = {
        {0, 0}, {1, 1}, {1, 0}, {0, 1}};
    auto x = intersection({0, 1, 2, 3}, points);
    for (auto y : x)
    {
        std::cout << "Key: (" << y.first.first << ", " << y.first.second << ") -> Values: ";
        for (const auto &val : y.second)
        {
            std::cout << "(" << val.first << ", " << val.second << ") ";
        }
        std::cout << std::endl;
    }
}