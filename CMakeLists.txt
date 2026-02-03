cmake_minimum_required(VERSION 3.16)
project(Resonance LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---------- Safety-grade DSP flags ----------
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(
        -O3
        -march=native
        -fno-fast-math
        -ffp-contract=off
        -Wall
        -Wextra
    )
endif()

# ---------- Dependencies ----------
find_package(PkgConfig REQUIRED)
pkg_check_modules(PORTAUDIO REQUIRED portaudio-2.0)
pkg_check_modules(FFTW3 REQUIRED fftw3)
pkg_check_modules(ZMQ REQUIRED libzmq)

# ---------- Subsystem Libraries ----------

add_library(ear src/ear.cpp)
target_include_directories(ear PUBLIC include ${PORTAUDIO_INCLUDE_DIRS})
target_link_libraries(ear PRIVATE ${PORTAUDIO_LIBRARIES})

add_library(safety src/safety.cpp)
target_include_directories(safety PUBLIC include)

add_library(filters src/filters.cpp)
target_include_directories(filters PUBLIC include)

add_library(fft_engine src/fft.cpp)
target_include_directories(fft_engine PUBLIC include ${FFTW3_INCLUDE_DIRS})
target_link_libraries(fft_engine PRIVATE ${FFTW3_LIBRARIES})

add_library(spectrogram src/spectrogram.cpp)
target_include_directories(spectrogram PUBLIC include)

add_library(broadcaster src/broadcaster.cpp)
target_include_directories(broadcaster PUBLIC include ${ZMQ_INCLUDE_DIRS})
target_link_libraries(broadcaster PRIVATE ${ZMQ_LIBRARIES})

# ---------- Main Node ----------

add_executable(resonance_node_a src/main.cpp)

target_link_libraries(resonance_node_a
    PRIVATE
        ear
        safety
        filters
        fft_engine
        spectrogram
        broadcaster
        pthread
)
