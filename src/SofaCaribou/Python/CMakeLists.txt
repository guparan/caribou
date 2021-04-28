project(SofaCaribou.Python)

set(HEADER_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/FictitiousGridElasticForce.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/FictitiousGridHyperelasticForcefield.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/HexahedronElasticForce.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/HyperelasticForcefield.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Ode/LegacyStaticODESolver.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Ode/StaticODESolver.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Solver/ConjugateGradientSolver.h
    ${CMAKE_CURRENT_SOURCE_DIR}/Topology/FictitiousGrid.h
)

set(SOURCE_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/SofaCaribou.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/FictitiousGridElasticForce.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/FictitiousGridHyperelasticForcefield.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/HexahedronElasticForce.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Forcefield/HyperelasticForcefield.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Ode/LegacyStaticODESolver.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Ode/StaticODESolver.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Solver/ConjugateGradientSolver.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/Topology/FictitiousGrid.cpp
)

set(PYTHON_FILES
    ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py
)

find_package(SofaPython3 REQUIRED)
find_package(Eigen3 REQUIRED)
#caribou_add_python_module(SofaCaribou
#                          TARGET_NAME       ${PROJECT_NAME}
#                          TARGET_ALIAS      Caribou::Python.SofaCaribou
#                          TARGET_DEPENDS    Caribou::Geometry Caribou::Python.Config SofaCaribou SofaPython3::Bindings.Sofa.Core Eigen3::Eigen
#                          COMPONENT_NAME    SofaCaribou
#                          PACKAGE_NAME      SofaCaribou
#                          DESTINATION       SofaCaribou
#                          SOURCE_FILES      ${SOURCE_FILES}
#                          PUBLIC_HEADERS    ${HEADER_FILES}
#                          PYTHON_FILES      ${PYTHON_FILES}
#                          PYTHON_TEST_FILES ${PYTHON_TEST_FILES}
#                          )

SP3_add_python_module(
    TARGET   ${PROJECT_NAME}
    PACKAGE  SofaCaribou
    MODULE   SofaCaribou
    SOURCES  ${SOURCE_FILES}
    HEADERS  ${HEADER_FILES}
    DEPENDS  Caribou::Geometry Caribou::Python.Config SofaCaribou SofaPython3::Bindings.Sofa.Core Eigen3::Eigen
)

if (NOT WIN32)
    # Avoid an annoying warning since the bindings code are in "caribou/bindings/*" but the headers are installed into
    # "Caribou/Bindings/*" to be consistent with SOFA and the rest of caribou libraries.
    target_compile_options(${PROJECT_NAME} PRIVATE "-Wno-nonportable-include-path")
endif()
