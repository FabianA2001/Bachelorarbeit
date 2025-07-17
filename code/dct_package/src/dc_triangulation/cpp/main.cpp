
#include <iostream>

#include "intersection.h"
#include "triangles.h"
#include "cadical_wrapper.h"
#include <cadical_binding/cadical_solver.h>
#include <cstdlib>

void intersection_test()
{
    const std::vector<std::pair<int, int>> points = {
        {0, 0}, {1, 1}, {1, 0}, {0, 1}};
    auto x = intersection({0, 1, 2, 3}, points, {});
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

void triangles_test()
{
    std::vector<Triangle_as_Node> triangles = {
        {0, 1, 2}, {0, 1, 3}, {1, 2, 3}, {0, 2, 3}};
    std::vector<Triangle_as_Point> triangles_pos = {
        {{0, 0}, {1, 1}, {1, 0}}, {{0, 0}, {1, 1}, {0, 1}}, {{1, 1}, {1, 0}, {0, 1}}, {{0, 0}, {1, 0}, {0, 1}}};

    auto result = triangles_intersection(triangles, triangles_pos);
    for (const auto &pair : result)
    {
        std::cout << "Triangle: (" << std::get<0>(pair.first) << ", " << std::get<1>(pair.first) << ", " << std::get<2>(pair.first) << ") -> Intersects with: ";
        for (const auto &tri : pair.second)
        {
            std::cout << "(" << std::get<0>(tri) << ", " << std::get<1>(tri) << ", " << std::get<2>(tri) << ") ";
        }
        std::cout << std::endl;
    }
}

void cadical_solver_test()
{
    int max_var = 6;
    std::vector<Vars_List> clauses = {
        {
            -1,
            -6,
        },
        {
            -6,
            -1,
        },
        {
            1,
            2,
        },
        {
            1,
            3,
        },
        {
            2,
            3,
        },
        {
            1,
            4,
        },
        {
            1,
            5,
        },
        {
            4,
            5,
        },
        {
            2,
        },
        {
            4,
        },
        {
            6,
        },
        {
            3,
        },
        {
            5,
        },
        {
            6,
        },
        {
            5,
        },
        {
            4,
        },
        {
            2,
        },
        {
            3,
        },
    };
    auto x = cadical_wrapper(max_var, clauses);
    int index = 0;
    for (const auto &val : x.first)
    {
        std::cout << "Variable " << index++ << ": " << val << "\n";
    }
}

int main()
{
    cadical_solver_test();
}