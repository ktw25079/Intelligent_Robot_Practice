"""turtlesim과 순찰 노드를 함께 실행하고 실행 인자로 주행 설정을 받는다."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    defaults = {
        'side_length': ('3.0', 'Length of each side'),
        'speed': ('2.0', 'Maximum forward speed'),
        'turn_speed': ('3.0', 'Maximum rotation speed'),
        'autostart': ('false', 'Start patrol without a service request'),
    }
    arguments = [DeclareLaunchArgument(name, default_value=value, description=description)
                 for name, (value, description) in defaults.items()]
    parameters = {
        name: ParameterValue(LaunchConfiguration(name), value_type=bool if name == 'autostart' else float)
        for name in defaults
    }
    return LaunchDescription(arguments + [
        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),
        Node(package='mission1_202402312', executable='patrol', name='patrol',
             output='screen', parameters=[parameters]),
    ])
