
#include <cadical_binding/cadical_solver.h>
#include <cstdlib>
#include <iostream>
// to check my assumptions on the workings of CaDiCaL; test with debug builds.
#include <cassert>
#include <unordered_map>

typedef std::vector<int> Vars_List;

// die erste Vars_list ist für die Finale Zuordnung, in dem zweiten Vector können zwischenzustände gespeichert werden
std::pair<Vars_List, std::vector<Vars_List>> cadical_wrapper(int number_vars,
                                                             int number_edges_vars,
                                                             std::vector<Vars_List> clauses,
                                                             bool save_state = false,
                                                             bool optimize_propagation = false);