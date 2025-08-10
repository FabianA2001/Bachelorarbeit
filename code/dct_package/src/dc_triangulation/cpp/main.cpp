
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
    std::vector<Vars_List> clauses = {
        {
            -4,
            -6,
        },
        {
            -4,
            -7,
        },
        {
            -6,
            -4,
        },
        {
            -6,
            -10,
        },
        {
            -6,
            -14,
        },
        {
            -7,
            -4,
        },
        {
            -10,
            -6,
        },
        {
            -10,
            -13,
        },
        {
            -13,
            -10,
        },
        {
            -14,
            -6,
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
            1,
            4,
        },
        {
            2,
            3,
        },
        {
            2,
            4,
        },
        {
            3,
            4,
        },
        {
            1,
            5,
        },
        {
            1,
            6,
        },
        {
            1,
            7,
        },
        {
            1,
            8,
        },
        {
            5,
            6,
        },
        {
            5,
            7,
        },
        {
            5,
            8,
        },
        {
            6,
            7,
        },
        {
            6,
            8,
        },
        {
            7,
            8,
        },
        {
            5,
            9,
        },
        {
            5,
            10,
        },
        {
            5,
            11,
        },
        {
            9,
            10,
        },
        {
            9,
            11,
        },
        {
            10,
            11,
        },
        {
            2,
            6,
        },
        {
            2,
            9,
        },
        {
            2,
            12,
        },
        {
            2,
            13,
        },
        {
            6,
            9,
        },
        {
            6,
            12,
        },
        {
            6,
            13,
        },
        {
            9,
            12,
        },
        {
            9,
            13,
        },
        {
            12,
            13,
        },
        {
            3,
            7,
        },
        {
            3,
            10,
        },
        {
            3,
            12,
        },
        {
            3,
            14,
        },
        {
            7,
            10,
        },
        {
            7,
            12,
        },
        {
            7,
            14,
        },
        {
            10,
            12,
        },
        {
            10,
            14,
        },
        {
            12,
            14,
        },
        {
            4,
            8,
        },
        {
            4,
            11,
        },
        {
            4,
            13,
        },
        {
            4,
            14,
        },
        {
            8,
            11,
        },
        {
            8,
            13,
        },
        {
            8,
            14,
        },
        {
            11,
            13,
        },
        {
            11,
            14,
        },
        {
            13,
            14,
        },
        {
            9,
        },
        {
            5,
        },
        {
            1,
        },
        {
            2,
        },
    };
    std::vector<Edge_raw> edges = {
        {
            {0, 0},
            {9, 0},
        },
        {
            {0, 0},
            {0, 9},
        },
        {
            {0, 0},
            {2, 3},
        },
        {
            {0, 0},
            {6, 6},
        },
        {
            {9, 0},
            {9, 9},
        },
        {
            {9, 0},
            {0, 9},
        },
        {
            {9, 0},
            {2, 3},
        },
        {
            {9, 0},
            {6, 6},
        },
        {
            {9, 9},
            {0, 9},
        },
        {
            {9, 9},
            {2, 3},
        },
        {
            {9, 9},
            {6, 6},
        },
        {
            {0, 9},
            {2, 3},
        },
        {
            {0, 9},
            {6, 6},
        },
        {
            {2, 3},
            {6, 6},
        },
    };
    std::unordered_map<std::string, int> node_to_sdegree = {
        {"0,0", 3},
        {"9,0", 4},
        {"9,9", 3},
        {"0,9", 4},
        {"2,3", 4},
        {"6,6", 4},
    };
    int max_var = 14;    // Maximum variable index in the clauses
    int edges_vars = 14; // Number of edge variables, can be adjusted as needed
    auto x = cadical_wrapper(max_var, edges_vars, clauses, edges, node_to_sdegree, false, true);
    int index = 1;
    for (const auto &val : x.first)
    {
        std::cout << "Variable " << index++ << ": " << val << "\n";
    }
    std::cout << "length of state saved: " << x.second.size() << "\n";
}

int main()
{
    cadical_solver_test();
}