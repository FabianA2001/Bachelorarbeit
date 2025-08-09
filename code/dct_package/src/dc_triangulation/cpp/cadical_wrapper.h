
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

typedef std::vector<int> Vars_List;
typedef std::pair<int, int> Point_raw;
typedef std::pair<Point_raw, Point_raw> Edge_raw;

// die erste Vars_list ist für die Finale Zuordnung, in dem zweiten Vector können zwischenzustände gespeichert werden
std::pair<Vars_List, std::vector<Vars_List>> cadical_wrapper(int number_vars,
                                                             int number_edges_vars,
                                                             std::vector<Vars_List> clauses,
                                                             std::vector<Edge_raw> edges = {},
                                                             bool save_state = false,
                                                             bool optimize_propagation = false);