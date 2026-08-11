cmake_minimum_required(VERSION 3.30)

set(CMAKE_CXX_STANDARD 23)

project(conformal_canvas)

cmake_policy(SET CMP0167 NEW)

set(Boost_USE_STATIC_LIBS ON)

find_package(OpenMP REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Boost 1.70 REQUIRED COMPONENTS url)
find_package(muparserx REQUIRED)

add_executable(conformal_canvas main.cpp
    conformal_warp_image.hpp
    network.hpp
    process_complex.hpp)
target_include_directories(conformal_canvas PRIVATE
    ${OpenCV_INCLUDE_DIRS}
    ${muparserx_INCLUDE_DIRS})
target_link_libraries(conformal_canvas PRIVATE
    ${OpenCV_LIBS}
    OpenMP::OpenMP_CXX
    Boost::boost
    Boost::url
    ${muparserx_LIBRARIES})
