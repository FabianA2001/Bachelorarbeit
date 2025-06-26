@echo Off

cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DBUILD_PYTHON_BINDINGS=Off -DCMAKE_TOOLCHAIN_FILE="build/generators/conan_toolchain.cmake"

cmake --build build


"./build/src/dc_triangulation/cpp/Debug/main_executable.exe"