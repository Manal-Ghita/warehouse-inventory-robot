cmake_minimum_required(VERSION 3.8)
project(entrepot_simulation)

find_package(ament_cmake REQUIRED)

# worlds et materials sont produits par outils/generer_entrepot.py
install(DIRECTORY worlds materials launch DESTINATION share/${PROJECT_NAME})

ament_package()
