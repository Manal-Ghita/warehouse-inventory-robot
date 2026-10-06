import os
import re

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

PKG = get_package_share_directory("robot_inventaire_description")


def description(context):
    mode = LaunchConfiguration("cameras").perform(context)
    urdf = xacro.process_file(os.path.join(PKG, "urdf", "robot.urdf.xacro"),
                              mappings={"cameras": mode}).toxml()
    # ros2_control ne supporte pas les commentaires (apostrophes) dans la description
    urdf = re.sub(r"<!--.*?-->", "", urdf, flags=re.DOTALL)
    return [Node(package="robot_state_publisher", executable="robot_state_publisher",
                 parameters=[{"robot_description": urdf, "use_sim_time": True}])]


def generate_launch_description():
    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py")))

    return LaunchDescription([
        DeclareLaunchArgument("cameras", default_value="test",
                              description="aucune, test ou toutes"),
        gazebo,
        OpaqueFunction(function=description),
        # pose le robot dans le monde a partir de sa description
        Node(package="gazebo_ros", executable="spawn_entity.py",
             arguments=["-topic", "robot_description", "-entity", "robot_inventaire"]),
        # demarre les controleurs une fois le robot pose
        Node(package="controller_manager", executable="spawner",
             arguments=["joint_state_broadcaster"]),
        Node(package="controller_manager", executable="spawner",
             arguments=["mat_controleur"]),
    ])