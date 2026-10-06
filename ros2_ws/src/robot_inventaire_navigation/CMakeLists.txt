cmake_minimum_required(VERSION 3.8)
project(robot_inventaire_navigation)

find_package(ament_cmake REQUIRED)

# config/nav2_params.yaml est produit par outils/creer_params.py
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})

ament_package()
