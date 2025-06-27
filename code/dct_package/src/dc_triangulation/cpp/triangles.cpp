#include "triangles.h"
// #include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Triangle_2.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/intersections.h>
#include <CGAL/Polygon_2.h>
#include <variant>
#include <CGAL/Object.h>

#include <iostream>
using namespace std;
// typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef CGAL::Exact_predicates_exact_constructions_kernel Kernel;
typedef CGAL::Point_2<Kernel> Point_own;
typedef CGAL::Triangle_2<Kernel> Triangle;

// Gibt die Fläche der Schnittmenge zweier Dreiecke zurück (0.0 falls keine oder nur punkt-/linienförmig)
double intersection_area(const Triangle &t1, const Triangle &t2)
{
    auto intersection_result = CGAL::intersection(t1, t2);
    if (!intersection_result)
        return 0.0;

    // Portable Lösung: Verwende CGAL::assign statt boost::get für bessere Kompatibilität
    Triangle tri;
    if (CGAL::assign(tri, *intersection_result))
        return CGAL::to_double(tri.area());
    
    std::vector<CGAL::Point_2<Kernel>> points;
    if (CGAL::assign(points, *intersection_result))
    {
        if (points.size() >= 3)
        {
            // Erstelle Polygon aus Punktvektor und berechne Fläche
            CGAL::Polygon_2<Kernel> poly(points.begin(), points.end());
            return CGAL::to_double(poly.area());
        }
    }
    return 0.0;
}

bool strictly_intersect(const Triangle &t1, const Triangle &t2)
{
    if (!CGAL::do_intersect(t1, t2))
        return false;
    auto x = intersection_area(t1, t2);
    return x > 0.0;
}

TriangleToTrianglesMap triangles_intersection(const std::vector<Triangle_as_Node> &triangles, const std::vector<Triangle_as_Point> &triangles_pos)
{
    TriangleToTrianglesMap result;

    // Iterate through each triangle
    for (int i = 0; i < triangles.size(); ++i)
    {
        // Convert the triangle to CGAL points
        Point_own p1(std::get<0>(triangles_pos.at(i)).first, std::get<0>(triangles_pos.at(i)).second);
        Point_own p2(std::get<1>(triangles_pos.at(i)).first, std::get<1>(triangles_pos.at(i)).second);
        Point_own p3(std::get<2>(triangles_pos.at(i)).first, std::get<2>(triangles_pos.at(i)).second);

        // Create a CGAL triangle
        Triangle cgal_triangle(p1, p2, p3);

        // Check for intersections with other triangles
        for (int j = 0; j < triangles.size(); ++j)
        {
            if (i == j)
            {
                continue; // Skip self-comparison
            }
            Point_own op1(std::get<0>(triangles_pos.at(j)).first, std::get<0>(triangles_pos.at(j)).second);
            Point_own op2(std::get<1>(triangles_pos.at(j)).first, std::get<1>(triangles_pos.at(j)).second);
            Point_own op3(std::get<2>(triangles_pos.at(j)).first, std::get<2>(triangles_pos.at(j)).second);

            Triangle cgal_other_triangle(op1, op2, op3);

            if (strictly_intersect(cgal_triangle, cgal_other_triangle))
            {
                result[triangles.at(i)].push_back(triangles.at(j));
            }
        }
    }
    return result;
}
