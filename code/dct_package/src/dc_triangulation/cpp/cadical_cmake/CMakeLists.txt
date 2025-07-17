enable_language(C)
enable_language(CXX)

include(CheckIPOSupported)
check_ipo_supported(RESULT LTO_SUPPORTED OUTPUT LTO_OUTPUT_DATA LANGUAGES C CXX)

try_compile(CDC_HAVE_FLEXIBLE_ARRAYS SOURCES "${CMAKE_CURRENT_LIST_DIR}/cadical_feature_tests/flexible.cpp")
try_compile(CDC_HAVE_UNLOCKED_IO SOURCES "${CMAKE_CURRENT_LIST_DIR}/cadical_feature_tests/unlocked_io.cpp")
try_compile(CDC_HAVE_CLOSEFROM SOURCES "${CMAKE_CURRENT_LIST_DIR}/cadical_feature_tests/closefrom.cpp")

add_library(cadical STATIC 
  "external/cadical/src/analyze.cpp"
  "external/cadical/src/arena.cpp"
  "external/cadical/src/assume.cpp"
  "external/cadical/src/averages.cpp"
  "external/cadical/src/backtrack.cpp"
  "external/cadical/src/backward.cpp"
  "external/cadical/src/bins.cpp"
  "external/cadical/src/block.cpp"
  "external/cadical/src/ccadical.cpp"
  "external/cadical/src/checker.cpp"
  "external/cadical/src/clause.cpp"
  "external/cadical/src/collect.cpp"
  "external/cadical/src/compact.cpp"
  "external/cadical/src/condition.cpp"
  "external/cadical/src/config.cpp"
  "external/cadical/src/constrain.cpp"
  "external/cadical/src/contract.cpp"
  "external/cadical/src/cover.cpp"
  "external/cadical/src/decide.cpp"
  "external/cadical/src/decompose.cpp"
  "external/cadical/src/deduplicate.cpp"
  "external/cadical/src/drattracer.cpp"
  "external/cadical/src/elim.cpp"
  "external/cadical/src/ema.cpp"
  "external/cadical/src/extend.cpp"
  "external/cadical/src/external.cpp"
  "external/cadical/src/external_propagate.cpp"
  "external/cadical/src/file.cpp"
  "external/cadical/src/flags.cpp"
  "external/cadical/src/flip.cpp"
  "external/cadical/src/format.cpp"
  "external/cadical/src/frattracer.cpp"
  "external/cadical/src/gates.cpp"
  "external/cadical/src/idruptracer.cpp"
  "external/cadical/src/instantiate.cpp"
  "external/cadical/src/internal.cpp"
  "external/cadical/src/ipasir.cpp"
  "external/cadical/src/lidruptracer.cpp"
  "external/cadical/src/limit.cpp"
  "external/cadical/src/logging.cpp"
  "external/cadical/src/lookahead.cpp"
  "external/cadical/src/lratbuilder.cpp"
  "external/cadical/src/lratchecker.cpp"
  "external/cadical/src/lrattracer.cpp"
  "external/cadical/src/lucky.cpp"
  "external/cadical/src/message.cpp"
  "external/cadical/src/minimize.cpp"
  "external/cadical/src/mobical.cpp"
  "external/cadical/src/occs.cpp"
  "external/cadical/src/options.cpp"
  "external/cadical/src/parse.cpp"
  "external/cadical/src/phases.cpp"
  "external/cadical/src/probe.cpp"
  "external/cadical/src/profile.cpp"
  "external/cadical/src/proof.cpp"
  "external/cadical/src/propagate.cpp"
  "external/cadical/src/queue.cpp"
  "external/cadical/src/random.cpp"
  "external/cadical/src/reap.cpp"
  "external/cadical/src/reduce.cpp"
  "external/cadical/src/rephase.cpp"
  "external/cadical/src/report.cpp"
  "external/cadical/src/resources.cpp"
  "external/cadical/src/restart.cpp"
  "external/cadical/src/restore.cpp"
  "external/cadical/src/score.cpp"
  "external/cadical/src/shrink.cpp"
  "external/cadical/src/signal.cpp"
  "external/cadical/src/solution.cpp"
  "external/cadical/src/solver.cpp"
  "external/cadical/src/stats.cpp"
  "external/cadical/src/subsume.cpp"
  "external/cadical/src/terminal.cpp"
  "external/cadical/src/ternary.cpp"
  "external/cadical/src/transred.cpp"
  "external/cadical/src/util.cpp"
  "external/cadical/src/var.cpp"
  "external/cadical/src/veripbtracer.cpp"
  "external/cadical/src/version.cpp"
  "external/cadical/src/vivify.cpp"
  "external/cadical/src/walk.cpp"
  "external/cadical/src/watch.cpp"
)
set_property(TARGET cadical PROPERTY POSITION_INDEPENDENT_CODE On)

if(NOT CDC_HAVE_FLEXIBLE_ARRAYS)
  target_compile_definitions(cadical PRIVATE "-DNFLEXIBLE")
endif()
if(NOT CDC_HAVE_UNLOCKED_IO)
  target_compile_definitions(cadical PRIVATE "-DNUNLOCKED")
endif()
if(NOT CDC_HAVE_CLOSEFROM)
  target_compile_definitions(cadical PRIVATE "-DNCLOSEFROM")
endif()
target_compile_definitions(cadical PRIVATE "-DNCONTRACTS" "-DNTRACING" "-DNCONTRIB" "-DNIPASIR")
target_include_directories(cadical PRIVATE "${CMAKE_CURRENT_LIST_DIR}/cadical_build_header")
target_compile_definitions(cadical PRIVATE COMPILER="${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")

add_library(cadical_binding STATIC "cadical_binding.cpp")
target_compile_definitions(cadical_binding PRIVATE "-DNCONTRACTS" "-DNTRACING" "-DNCONTRIB" "-DNIPASIR")
target_link_libraries(cadical_binding PUBLIC cadical)
target_include_directories(cadical_binding PRIVATE "${CMAKE_CURRENT_LIST_DIR}/cadical_build_header"
                                                   "${CMAKE_CURRENT_LIST_DIR}/external/cadical/src")

# include the public header directory in the source tree when building the lib
# include the include directory when using the installed lib
target_include_directories(cadical_binding PUBLIC 
  $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/include> 
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)    

if(LTO_SUPPORTED)
  set_property(TARGET cadical PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
  set_property(TARGET cadical PROPERTY INTERPROCEDURAL_OPTIMIZATION_DEBUG FALSE)
  set_property(TARGET cadical_binding PROPERTY INTERPROCEDURAL_OPTIMIZATION TRUE)
  set_property(TARGET cadical_binding PROPERTY INTERPROCEDURAL_OPTIMIZATION_DEBUG FALSE)
endif()
