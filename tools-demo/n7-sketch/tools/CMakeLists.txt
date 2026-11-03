# Builds mm_harness against a Monster Mash checkout: cmake -DMM=<path to monster-mash> <this dir>
cmake_minimum_required(VERSION 3.5)
project(mm_harness LANGUAGES CXX C)
set(S ${MM}/src)
set(T ${MM}/third_party)
find_package(SDL2 REQUIRED)
find_package(OpenGL REQUIRED)
add_executable(mm_harness mm_harness.cpp
  ${S}/defengarapl.cpp ${S}/cpanim.cpp ${S}/loadsave.cpp ${S}/reconstruction.cpp ${S}/mypainter.cpp ${S}/mywindow.cpp ${S}/def3dsdl.cpp
  ${T}/ir3d-utils/regionToMesh.cpp ${T}/ir3d-utils/MeshBuilder.cpp ${T}/image/imageReadWrite.cpp ${T}/image/imageScale.cpp
  ${T}/image/imageUtils.cpp ${T}/miscutils/def3d.cpp ${T}/miscutils/mesh3d.cpp ${T}/miscutils/fsutils.cpp
  ${T}/miscutils/opengltools.cpp ${T}/miscutils/camera.cpp ${T}/triangle/triangle.c ${T}/zip-mod/zip.c
  ${T}/SDL2_gfx-mod/SDL2_gfxPrimitives-mod.c ${T}/SDL2_gfx/SDL2_rotozoom.c)
# the same definitions, include paths and flags as Monster Mash's own CMakeLists (desktop build)
target_compile_definitions(mm_harness PRIVATE IMAGE_READ_WRITE IMAGE_MINIZ_EXTERNAL IMAGE_SCALE TRILIBRARY NO_TIMER
  IGL_PARALLEL_FOR_FORCE_SERIAL EIGEN_MPL2_ONLY EIGEN_SPARSESOLVERBASE_H _SDL2_gfxPrimitives_h
  APP_VERSION=260311 USE_SDL_GLES2 USE_OPENGL_FOR_DRAWING_INSTEAD_OF_SDL)
target_include_directories(mm_harness PRIVATE ${S} ${T} ${T}/eigen3-mod ${T}/eigen3 ${T}/libigl/include ${T}/stb ${T}/triangle
  ${T}/zip-mod ${T}/SDL2_gfx ${T}/SDL2_gfx-mod ${SDL2_INCLUDE_DIRS})
set(CMAKE_CXX_STANDARD 17)
target_compile_features(mm_harness PRIVATE cxx_std_17)
target_compile_options(mm_harness PRIVATE -Wno-sign-compare -Werror=return-type -Wno-narrowing)
target_link_libraries(mm_harness ${SDL2_LIBRARIES} ${OPENGL_LIBRARIES} -lpthread)
