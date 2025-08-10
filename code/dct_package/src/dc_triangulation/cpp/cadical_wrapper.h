
#include <cadical_binding/cadical_solver.h>
#include <cstdlib>
#include <iostream>
// to check my assumptions on the workings of CaDiCaL; test with debug builds.
#include <cassert>
#include <unordered_map>

#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/convex_hull_2.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Arrangement_2.h>
#include <CGAL/Arr_segment_traits_2.h>

typedef int Number_type;
typedef CGAL::Simple_cartesian<Number_type> Kernel;
typedef CGAL::Arr_segment_traits_2<Kernel> Traits_2;
typedef Traits_2::Point_2 Point_2;
typedef Traits_2::X_monotone_curve_2 Segment_2;
typedef CGAL::Arrangement_2<Traits_2> Arrangement_2;
typedef Arrangement_2::Vertex_handle Vertex_handle;
typedef Arrangement_2::Halfedge_handle Halfedge_handle;
typedef Arrangement_2::Face_handle Face_handle;

typedef std::vector<int> Vars_List;
typedef std::pair<int, int> Point_raw;
typedef std::pair<Point_raw, Point_raw> Edge_raw;
// die erste Vars_list ist für die Finale Zuordnung, in dem zweiten Vector können zwischenzustände gespeichert werden
std::pair<Vars_List, std::vector<Vars_List>> cadical_wrapper(int number_vars,
                                                             int number_edges_vars,
                                                             std::vector<Vars_List> clauses,
                                                             std::vector<Edge_raw> edges = {},
                                                             std::unordered_map<std::string, int> node_to_sdegree = {},
                                                             bool save_state = false,
                                                             bool optimize_propagation = false);