
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        # 启动 Turtlesim 仿真节点
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim'
        ),

        # 启动 Action Server
        Node(
            package='turtle_action_demo',
            executable='action_server',
            name='turtle_action_server',
            output='screen'
        ),


    ])
