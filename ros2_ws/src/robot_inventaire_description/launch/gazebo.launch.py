import os, re

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory("robot_inventaire_description")
    urdf = xacro.process_file(os.path.join(pkg, "urdf", "robot.urdf.xacro")).toxml()
    # ros2_control ne supporte pas les commentaires (apostrophes) dans la description
    urdf = re.sub(r"<!--.*?-->", "", urdf, flags=re.DOTALL)

    gazebo = IncludeLaunchDescription(PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py")))

    return LaunchDescription([
        gazebo,
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": urdf, "use_sim_time": True}]),
        # pose le robot dans le monde a partir de sa description
        Node(package="gazebo_ros", executable="spawn_entity.py",
             arguments=["-topic", "robot_description", "-entity", "robot_inventaire"]),
        # demarre les controleurs une fois le robot pose
        Node(package="controller_manager", executable="spawner",
             arguments=["joint_state_broadcaster"]),
        Node(package="controller_manager", executable="spawner",
             arguments=["mat_controleur"]),
    ])