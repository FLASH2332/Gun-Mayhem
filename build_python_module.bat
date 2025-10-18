@echo off
REM Build the Python module for Gun Mayhem

if not exist build_pybind mkdir build_pybind
cd build_pybind

REM Copy the pybind CMakeLists.txt
copy ..\CMakeLists_pybind.txt CMakeLists.txt

cmake . -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
if %ERRORLEVEL% NEQ 0 (
    echo CMake configuration failed!
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

mingw32-make
if %ERRORLEVEL% NEQ 0 (
    echo Build failed!
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Python module built successfully!
echo The gunmayhem.pyd file is in the build_pybind directory
echo.
cd ..
pause
