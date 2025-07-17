# Created by the script cgal_create_cmake_script This is the CMake script for
# compiling a CGAL application.

find_package(CGAL REQUIRED)
add_subdirectory("cadical_cmake")

if(BUILD_PYTHON_BINDINGS)
    # Python bindings using pybind11
    cpmaddpackage("gh:pybind/pybind11@2.13.6") # pybind11, essential
    
    pybind11_add_module(_cpp_bindings bindings.cpp intersection.cpp triangles.cpp cadical_wrapper.cpp)
    target_link_libraries(_cpp_bindings PUBLIC CGAL::CGAL) 
    # enable compilation warnings
    target_compile_options(
      _cpp_bindings PRIVATE "$<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:-Wall>")
    target_compile_definitions(_cpp_bindings
                               PRIVATE PYBIND11_DETAILED_ERROR_MESSAGES)
    
    # move the compiled module to this folder. You can check with `python setup.py
    # build` how the package will look like and if the module is moved to the right
    # location.
    install(TARGETS _cpp_bindings DESTINATION ./src/dc_triangulation/cpp)
else()
    # Native C++ executable
    add_executable(main_executable main.cpp  intersection.cpp triangles.cpp cadical_wrapper.cpp)
    target_link_libraries(main_executable PUBLIC CGAL::CGAL)
    target_link_libraries(main_executable PUBLIC cadical_binding)
    
    # enable compilation warnings
    target_compile_options(
      main_executable PRIVATE "$<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:-Wall>")
    
    # Install the executable
    install(TARGETS main_executable DESTINATION .)
endif()
