import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    ent = get_package_share_directory("entrepot_simulation")
    desc = get_package_share_directory("robot_inventaire_description")

    return LaunchDescription([
        DeclareLaunchArgument("cameras", default_value="test",
                              description="aucune, test ou toutes"),
        # materiaux de gazebo + textures des etiquettes
        AppendEnvironmentVariable("GAZEBO_RESOURCE_PATH", "/usr/share/gazebo-11"),
        AppendEnvironmentVariable("GAZEBO_RESOURCE_PATH", ent),
        # robot dans l'allee transversale, face a l'allee 1
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(desc, "launch", "gazebo.launch.py")),
            launch_arguments={
                "world": os.path.join(ent, "worlds", "entrepot.world"),
                "cameras": LaunchConfiguration("cameras"),
                "x": "-2.0", "y": "1.495", "yaw": "0.0",
            }.items()),
    ])
