cmake_minimum_required(VERSION 3.14)
project(__PROJECT_NAME__ C CXX)

# Enforce clean, standard-compliant build rules
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Discover generated code layout
file(GLOB GENERATED_SOURCES "generated/*.c")

add_executable(__PROJECT_NAME__ 
    main.cpp 
    ${GENERATED_SOURCES}
)

target_include_directories(__PROJECT_NAME__ PRIVATE "generated")

# Ensure both C and C++ components compile safely
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(__PROJECT_NAME__ PRIVATE -Wall -Wextra -Wpedantic)
elseif(MSVC)
    target_compile_options(__PROJECT_NAME__ PRIVATE /W4)
endif()
