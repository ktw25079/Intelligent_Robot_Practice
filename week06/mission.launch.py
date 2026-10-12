"""Lecture 06: actual Gazebo simulation, RViz LaserScan and RQt Plot."""
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    root=Path(__file__).resolve().parent
    gazebo=Path(get_package_share_directory('turtlebot3_manipulation_gazebo'))
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(str(gazebo/'launch/gazebo.launch.py'))),
        TimerAction(period=12., actions=[
            Node(package='rviz2',executable='rviz2',arguments=['-d',str(root/'mission.rviz')],parameters=[{'use_sim_time':True}]),
            Node(package='rqt_plot',executable='rqt_plot',arguments=['--empty','/cmd_vel/linear/x','/cmd_vel/angular/z']),
        ]),
    ])
