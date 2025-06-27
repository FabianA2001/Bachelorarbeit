
#include "triangles.h"
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangle_2.h>
#include <CGAL/Simple_cartesian.h>
#include <CGAL/intersections.h>
#include <variant>



#include <iostream>
using namespace std;
typedef CGAL::Exact_predicates_inexact_constructions_kernel Kernel;
typedef CGAL::Point_2<Kernel> Point_own;
typedef CGAL::Triangle_2<Kernel> Triangle;

bool strictly_intersect(const  Triangle & t1, const Triangle& t2) {
    return false;
}

TriangleToTrianglesMap triangles_intersection(const std::vector<Triangle_as_Node> &triangles , const std::vector<Triangle_as_Point> &triangles_pos){
    TriangleToTrianglesMap result;

    // Iterate through each triangle
    for (int i = 0; i < triangles.size(); ++i) {
        // Convert the triangle to CGAL points
        Point_own p1(std::get<0>(triangles_pos.at(i)).first, std::get<0>(triangles_pos.at(i)).second);
        Point_own p2(std::get<1>(triangles_pos.at(i)).first, std::get<1>(triangles_pos.at(i)).second);
        Point_own p3(std::get<2>(triangles_pos.at(i)).first, std::get<2>(triangles_pos.at(i)).second);

        // Create a CGAL triangle
        Triangle cgal_triangle(p1, p2, p3);

        // Check for intersections with other triangles
        for (int j = 0; j < triangles.size(); ++j) {
            if (i == j) {
                continue; // Skip self-comparison
            }
            Point_own op1(std::get<0>(triangles_pos.at(j)).first, std::get<0>(triangles_pos.at(j)).second);
            Point_own op2(std::get<1>(triangles_pos.at(j)).first, std::get<1>(triangles_pos.at(j)).second);
            Point_own op3(std::get<2>(triangles_pos.at(j)).first, std::get<2>(triangles_pos.at(j)).second);

            Triangle cgal_other_triangle(op1, op2, op3);

            if (strictly_intersect(cgal_triangle, cgal_other_triangle)) {
                result[triangles.at(i)].push_back(triangles.at(j));
            }
        }
    }
    return result;
}

