## Installation für Entwicklung
### Python
1. `python setup.py develop`
2. bei Fehler : `pip install skbuild_conan` oder `conan install . --build=missing -of . -s build_type=Debug -s compiler.cppstd=17`
3. `pip install -e .`


Wenn der cpp code verändert wird wieder `python setup.py develop`

### CPP

Submodule cardial installation
1. `git submodule update --init --recursive`
2. `python setup.py develop`

3. `conan install . --build=missing -of . -s build_type=Debug -s compiler.cppstd=17`
4. MacOS: `cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DBUILD_PYTHON_BINDINGS=Off -DCMAKE_TOOLCHAIN_FILE=build/Debug/generators/conan_toolchain.cmake`
   
   Windows: `cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DBUILD_PYTHON_BINDINGS=Off -DCMAKE_TOOLCHAIN_FILE="build/generators/conan_toolchain.cmake"`

5. `cmake --build build`
6. Path Excutable:
 
    Windows: `"./build/src/dc_triangulation/cpp/Debug/main_executable.exe"`
    
    MacOs: `./build/src/dc_triangulation/cpp/main_executable`

