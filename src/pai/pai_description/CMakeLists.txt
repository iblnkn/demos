cmake_minimum_required(VERSION 3.10)
project(pai_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)

install(
  DIRECTORY world
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # conda-forge libxml2 lacks HTTP; xmllint can't fetch remote schemas
  list(APPEND AMENT_LINT_AUTO_EXCLUDE ament_cmake_xmllint)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
