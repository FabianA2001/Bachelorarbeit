
#include <iostream>

#include "intersection.h"
#include "triangles.h"

void intersection_test(){
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

void triangles_test(){
    std::vector<Triangle_as_Node> triangles = {
        {0, 1, 2}, {0, 1, 3}, {1, 2, 3}, {0, 2, 3}};
    std::vector<Triangle_as_Point> triangles_pos = {
        {{0, 0}, {1, 1}, {1, 0}}, {{0, 0}, {1, 1}, {0, 1}}, {{1, 1}, {1, 0}, {0, 1}}, {{0, 0}, {1, 0}, {0, 1}}};

    auto result = triangles_intersection(triangles, triangles_pos);
    for (const auto &pair : result) {
        std::cout << "Triangle: (" << std::get<0>(pair.first) << ", " << std::get<1>(pair.first) << ", " << std::get<2>(pair.first) << ") -> Intersects with: ";
        for (const auto &tri : pair.second) {
            std::cout << "(" << std::get<0>(tri) << ", " << std::get<1>(tri) << ", " << std::get<2>(tri) << ") ";
        }
        std::cout << std::endl;
    }
}

int main()
{
    std::cout << "Running intersection test..." << std::endl;
    triangles_test();
}