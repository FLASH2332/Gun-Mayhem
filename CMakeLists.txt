cmake_minimum_required(VERSION 3.15)
project(GunMayhem)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Collect source files
file(GLOB_RECURSE SOURCES
    "${CMAKE_SOURCE_DIR}/src/*.cpp"
    "${CMAKE_SOURCE_DIR}/main.cpp"
)

# Collect header files
file(GLOB_RECURSE HEADERS
    "${CMAKE_SOURCE_DIR}/include/*.hpp"
)

# Create the executable
add_executable(GunMayhem ${SOURCES} ${HEADERS})

# set base dirs
set(SDL2_DIR ${CMAKE_SOURCE_DIR}/libs/SDL2-2.32.8/x86_64-w64-mingw32)
set(JSON_DIR ${CMAKE_SOURCE_DIR}/libs/nlohmannjson)
set(SDL2_TTF_DIR ${CMAKE_SOURCE_DIR}/libs/SDL2_ttf-2.24.0/x86_64-w64-mingw32)

# Include directories
target_include_directories(GunMayhem PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${SDL2_DIR}/include/SDL2
    ${JSON_DIR}/include
    ${SDL2_TTF_DIR}/include/SDL2
)

# Link SDL2 libraries (no g++/MinGW specific flags)
target_link_directories(GunMayhem PRIVATE
    ${SDL2_DIR}/lib
    ${SDL2_TTF_DIR}/lib
)

# Link libraries
target_link_libraries(GunMayhem
    SDL2
    SDL2main
    SDL2_ttf
)

# Optional: Copy SDL2.dll to the output directory
add_custom_command(TARGET GunMayhem POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${SDL2_DIR}/bin/SDL2.dll
        $<TARGET_FILE_DIR:GunMayhem>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${SDL2_TTF_DIR}/bin/SDL2_ttf.dll
        $<TARGET_FILE_DIR:GunMayhem>
)
