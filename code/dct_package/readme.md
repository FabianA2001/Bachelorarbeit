## Installation für Entwicklung
### Python
1. `python setup.py develop`
2. bei Fehler : `pip install skbuild_conan` 
3. `pip install -e .`


Wenn der cpp code verändert wird wieder `python setup.py develop`

### CPP

1. `conan install . --build=missing -of . -s build_type=Debug`
2. `cmake -B build -S . -DCMAKE_BUILD_TYPE=Debug -DBUILD_PYTHON_BINDINGS=Off -DCMAKE_TOOLCHAIN_FILE=build/Debug/generators/conan_toolchain.cmake`
3. `cmake --build build`
