from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, PushRosNamespace

def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    sub_reliability = LaunchConfiguration('subscriber_reliability')

    # Формируем правильный абсолютный путь к топику в виде строки
    topic_name = PythonExpression(["'/", namespace, "/sensor_pose'"])

    return LaunchDescription([
        DeclareLaunchArgument('namespace', default_value='robot_a'),
        DeclareLaunchArgument('record', default_value='false'),
        DeclareLaunchArgument('bag_dir', default_value='evidence/pr05/bag'),
        DeclareLaunchArgument('subscriber_reliability', default_value='reliable'),

        Node(package='turtlesim', executable='turtlesim_node', name='turtlesim'),

        GroupAction([
            PushRosNamespace(namespace),
            Node(
                package='patrol',
                executable='patrol',
                remappings=[('cmd_vel', '/turtle1/cmd_vel')]
            ),
            Node(package='course_bringup', executable='pose_relay', name='pose_relay'),
            Node(
                package='course_bringup',
                executable='pose_listener',
                name='pose_listener',
                parameters=[{'reliability': sub_reliability}]
            )
        ]),

        ExecuteProcess(
            condition=IfCondition(record),
            cmd=['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag_dir, '--topics', topic_name,
                 '--qos-profile-overrides-path', 'src/course_bringup/config/qos-overrides.yaml'],
            output='screen'
        )
    ])
