import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    nav = get_package_share_directory("robot_inventaire_navigation")
    bringup = get_package_share_directory("nav2_bringup")
    slam = get_package_share_directory("slam_toolbox")
    params = os.path.join(nav, "config", "nav2_params.yaml")

    return LaunchDescription([
        # carte construite en direct avec le lidar
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(slam, "launch", "online_async_launch.py")),
            launch_arguments={"use_sim_time": "True"}.items()),
        # navigation sur la carte en cours de construction
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(bringup, "launch", "navigation_launch.py")),
            launch_arguments={"use_sim_time": "True", "params_file": params}.items()),
        Node(package="rviz2", executable="rviz2",
             arguments=["-d", os.path.join(bringup, "rviz", "nav2_default_view.rviz")],
             parameters=[{"use_sim_time": True}]),
    ])
