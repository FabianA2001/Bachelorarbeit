# Cadical wrapped with CMake build system
Should build out-of-the-box (with Clang/GCC).
CaDiCaL itself is contained as a submodule in the `external/cadical` directory,
so make sure to close the submodule.
The library itself should be usable via `add_subdirectory(cadical-cmake)`
and linked with `target_link_libraries(my_target cadical_binding)`.

## Examples
There are two examples in the `examples` directory.
They can be built within the `examples` directory:
```bash 
mkdir -p build/Release
cmake -S . -B build/Release -DCMAKE_BUILD_TYPE=Release
cmake --build build/Release --parallel 4
```

Example 2 gives a naive example of using external propagators,
while printing which of the callback routines are called (and how).