#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For automatic conversion between STL and Python types
#include "intersection.h"
#include "triangles.h"
#include "cadical_wrapper.h"

PYBIND11_MODULE(_cpp_bindings, m)
{
      m.doc() = "pybind11 example plugin"; // optional module docstring

      // Exposing the intersection function to Python
      m.def("intersection", &intersection, "Function that processes a list of point pairs and returns intersection map",
            pybind11::arg("indices"), pybind11::arg("point_pairs"), pybind11::arg("impossible_edges"));

      m.def("triangles_intersection", &triangles_intersection,
            "Function that processes triangles and their positions to find intersections",
            pybind11::arg("triangles"), pybind11::arg("triangles_pos"));

      m.def("max_clique", &max_clique,
            "Function that finds the maximum cliques in a graph represented by an intersection map",
            pybind11::arg("intersection_map"));

      m.def("cadical_wrapper", &cadical_wrapper,
            "Function that wraps the CaDiCaL SAT solver",
            pybind11::arg("number_vars"), pybind11::arg("clauses"));
}