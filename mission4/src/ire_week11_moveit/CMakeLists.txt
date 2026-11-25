cmake_minimum_required(VERSION 3.8)
project(ire_week11_moveit)
find_package(ament_cmake REQUIRED)
install(PROGRAMS scripts/pick_demo_202302200.py
  DESTINATION lib/${PROJECT_NAME} RENAME pick_demo_202302200)
ament_package()
