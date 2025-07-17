
#include <iostream>

#include "intersection.h"
#include "triangles.h"
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

int main()
{
    cdc::CadicalSolver solver;
    using Lit = cdc::CadicalSolver::Lit;
    Lit x1 = solver.new_var();
    Lit x2 = solver.new_var();
    Lit x3 = solver.new_var();

    solver.add_short_clause(x1);
    // x1 -> x2
    solver.add_short_clause(-x1, x2);

    // x1 -> x2 v -x3
    solver.add_short_clause(-x1, x2, -x3);

    std::optional<bool> result = solver.solve();
    if (!result)
    {
        // timeout or interrupt. should not happen here
        std::cerr << "INCORRECT INTERRUPT/TIMEOUT\n";
        return EXIT_FAILURE;
    }
    if (!*result)
    {
        // UNSAT - should not happen here
        std::cerr << "INCORRECT UNSAT!\n";
        return EXIT_FAILURE;
    }

    auto sat_assignment = solver.get_model();

    for (auto const &var : {x1, x2, x3})
    {
        std::cout << "sat[" << var << "] = " << sat_assignment[var] << "\n";
    }
}