# Plug-and-play parameters.
set(PROJ_ROOT ".")
set(EXEC_NAME "asmld")

# Std CMake preamble.
cmake_minimum_required(VERSION 3.14)
project(${EXEC_NAME})

# Gather files/paths (globbing because i'm lazy/arrogant).
file(GLOB build_sources
	${PROJ_ROOT}/src/main.cpp
	${PROJ_ROOT}/src/*/*.cpp
)
file(GLOB build_includes
	${PROJ_ROOT}/inc
)

# Add souces/includes to build.
add_executable(${EXEC_NAME}
	${build_sources}
)
target_include_directories(${EXEC_NAME} PUBLIC
	${build_includes}
)
