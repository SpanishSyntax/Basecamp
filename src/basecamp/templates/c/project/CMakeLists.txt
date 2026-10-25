
cmake_minimum_required(VERSION 3.14)
project(__PROJECT_NAME__ C)

# Enforce strict, portable C99 standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF) 

# Discover generated code layout
file(GLOB GENERATED_SOURCES "generated/*.c")

add_executable(__PROJECT_NAME__ 
    main.c
    ${GENERATED_SOURCES}
)

target_include_directories(__PROJECT_NAME__ PRIVATE "generated")

# Guard against unsafe generator output with strict warnings
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(__PROJECT_NAME__ PRIVATE -Wall -Wextra -Wpedantic)
elseif(MSVC)
    target_compile_options(__PROJECT_NAME__ PRIVATE /W4)
endif()
