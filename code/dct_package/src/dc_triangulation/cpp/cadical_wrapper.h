
#include <cadical_binding/cadical_solver.h>
#include <cstdlib>
#include <iostream>
// to check my assumptions on the workings of CaDiCaL; test with debug builds.
#include <cassert>
#include <unordered_map>

std::vector<int> cadical_wrapper(int nummber_vars, std::vector<std::vector<int>> clauses);