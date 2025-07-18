## Installation für Entwicklung
### Python
1. `git submodule update --init --recursive`
2. `python setup.py develop`
3. bei Fehler : `pip install skbuild_conan` oder `conan install . --build=missing -of . -s build_type=Debug -s compiler.cppstd=17`
4. `pip install -e .`


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





### vscode config

MIMode anpassen, macOS: `lldb` und linux: `gdb` (bei mir)

launch.json
```json
{
    "version": "1.0.0",
    "configurations": [
        {
            "name": "Debug C++ (main_executable)",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/dct_package/build/src/dc_triangulation/cpp/main_executable",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/dct_package",
            "environment": [],
            "externalConsole": false,
            "MIMode": "lldb",
            "preLaunchTask": "Build Debug",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "logging": {
                "engineLogging": false
            }
        },
        {
            "name": "Debug Python (run_dct.py)",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/run_dct/run_dct.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/run_dct",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/dct_package"
            },
            "justMyCode": false
        }
    ]
}
```

tasks.json
```json
{
    "version": "1.0.0",
    "tasks": [
        {
            "label": "Build Debug",
            "type": "shell",
            "command": "cmake",
            "args": [
                "--build",
                "build",
                "--config",
                "Debug"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "dependsOn": "Configure CMake",
            "options": {
                "cwd": "${workspaceFolder}/dct_package"
            },
            "problemMatcher": [
                "$gcc"
            ],
            "detail": "Build the C++ project in Debug mode"
        }
    ]
}
```