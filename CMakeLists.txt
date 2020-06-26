cmake_minimum_required(VERSION 3.10)

project(util_tools)

if (CMAKE_SIZEOF_VOID_P EQUAL 4)
    set(EXE_POSTFIX 32)
else()
    set(EXE_POSTFIX 64)
endif()

add_executable(runas${EXE_POSTFIX} runas.cpp)
add_executable(crash${EXE_POSTFIX} crash.cpp)