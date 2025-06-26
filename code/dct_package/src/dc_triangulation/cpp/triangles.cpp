
#include "triangles.h"
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangle_2.h>

TriangleToTrianglesMap triangles_intersection(const std::vector<Triangle_as_Node> &triangles , const std::vector<Triangle_as_Point> &triangles_pos){
    TriangleToTrianglesMap result;

    // Iterate through each triangle
    for (int i = 0; i < triangles.size(); ++i) {
        // Convert the triangle to CGAL points
        CGAL::Point_2<CGAL::Exact_predicates_inexact_constructions_kernel> p1(std::get<0>(triangles_pos.at(i)).first, std::get<0>(triangles_pos.at(i)).second);
        CGAL::Point_2<CGAL::Exact_predicates_inexact_constructions_kernel> p2(std::get<1>(triangles_pos.at(i)).first, std::get<1>(triangles_pos.at(i)).second);
        CGAL::Point_2<CGAL::Exact_predicates_inexact_constructions_kernel> p3(std::get<2>(triangles_pos.at(i)).first, std::get<2>(triangles_pos.at(i)).second);

        // Create a CGAL triangle
        CGAL::Triangle_2<CGAL::Exact_predicates_inexact_constructions_kernel> cgal_triangle(p1, p2, p3);

        // Check for intersections with other triangles
        for (int j = 0; j < triangles.size(); ++j) {
            if (i != j) {
                CGAL::Point_2<CGAL::Exact_predicates_inexact_constructions_kernel> op1(std::get<0>(triangles_pos.at(j)).first, std::get<0>(triangles_pos.at(j)).second);
                CGAL::Point_2<CGAL::Exact_predicates_inexact_constructions_kernel> op2(std::get<1>(triangles_pos.at(j)).first, std::get<1>(triangles_pos.at(j)).second);
                CGAL::Point_2<CGAL::Exact_predicates_inexact_constructions_kernel> op3(std::get<2>(triangles_pos.at(j)).first, std::get<2>(triangles_pos.at(j)).second);

                CGAL::Triangle_2<CGAL::Exact_predicates_inexact_constructions_kernel> cgal_other_triangle(op1, op2, op3);

                // Check if the triangles properly intersect (not just touch)
                // We need to verify that the triangles have overlapping interiors
                if (CGAL::do_intersect(cgal_triangle, cgal_other_triangle)) {
                    // Additional check: ensure it's not just touching at boundaries
                    // Check if any vertex of one triangle is inside the other triangle
                    bool proper_intersection = false;
                    
                    // Check if any vertex of triangle j is inside triangle i
                    if (cgal_triangle.has_on_positive_side(op1) || 
                        cgal_triangle.has_on_positive_side(op2) || 
                        cgal_triangle.has_on_positive_side(op3)) {
                        proper_intersection = true;
                    }
                    
                    // Check if any vertex of triangle i is inside triangle j
                    if (!proper_intersection && 
                        (cgal_other_triangle.has_on_positive_side(p1) || 
                         cgal_other_triangle.has_on_positive_side(p2) || 
                         cgal_other_triangle.has_on_positive_side(p3))) {
                        proper_intersection = true;
                    }
                    
                    if (proper_intersection) {
                        result[triangles.at(i)].push_back(triangles.at(j));
                    }
                }
            }
        }
    }

    return result;
}

