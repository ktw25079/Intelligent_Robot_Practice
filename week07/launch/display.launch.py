import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    week_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf = os.path.join(week_dir, 'myurdf_202302200.urdf')
    desc = ParameterValue(Command(['cat ', LaunchConfiguration('model')]), value_type=str)
    return LaunchDescription([
        DeclareLaunchArgument('model', default_value=urdf,
                              description='Absolute path to the URDF file'),
        DeclareLaunchArgument('rvizconfig', default_value=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'display.rviz')),
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             parameters=[{'robot_description': desc}]),
        Node(package='joint_state_publisher_gui', executable='joint_state_publisher_gui'),
        Node(package='rviz2', executable='rviz2',
             arguments=['-d', LaunchConfiguration('rvizconfig')]),
    ])
