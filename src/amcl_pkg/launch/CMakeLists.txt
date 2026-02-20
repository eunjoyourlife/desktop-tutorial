cmake_minimum_required(VERSION 3.8)
project(amcl_pkg)

find_package(ament_cmake REQUIRED)

# launch / config 파일 설치
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
