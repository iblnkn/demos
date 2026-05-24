#!/usr/bin/env python3

# Copyright 2026 Isaac Blankenau
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""
Top-level data collection launch: follower arm + cameras + leader teleop + episode recorder.

Composes the three sub-launch files, passing top-level arguments down.
Any argument declared here takes precedence over defaults in child launches.

Usage:
    ros2 launch pai_bringup data_collection.launch.py

    # Override bag output directory
    ros2 launch pai_bringup data_collection.launch.py bag_base_dir:=my_dataset/bags

    # Different arm ports
    ros2 launch pai_bringup data_collection.launch.py \
        follower_port:=/dev/ttyACM0 leader_port:=/dev/ttyACM1
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


DEFAULT_LEADER_CONTROLLERS = PathJoinSubstitution(
    [
        FindPackageShare('pai_leader_teleop'),
        'config',
        'control',
        'ros2_controllers_leader.yaml',
    ]
)

DEFAULT_LEADER_DESCRIPTION = PathJoinSubstitution(
    [
        FindPackageShare('pai_leader_teleop'),
        'urdf',
        'so_arm_leader.urdf.xacro',
    ]
)

DEFAULT_LEADER_ROS2_CONTROL = PathJoinSubstitution(
    [
        FindPackageShare('pai_leader_teleop'),
        'config',
        'control',
        'so_arm101_leader.ros2_control.xacro',
    ]
)


def launch_setup(context, *args, **kwargs):
    """Resolve arguments and compose sub-launches."""
    follower_port = LaunchConfiguration('follower_port').perform(context)
    leader_port = LaunchConfiguration('leader_port').perform(context)
    contract_path = LaunchConfiguration('contract_path').perform(context)
    bag_base_dir = LaunchConfiguration('bag_base_dir').perform(context)
    launch_rviz = LaunchConfiguration('launch_rviz').perform(context)
    use_cameras = LaunchConfiguration('use_cameras').perform(context)
    follower_joint_config = LaunchConfiguration('follower_joint_config').perform(context)
    leader_joint_config = LaunchConfiguration('leader_joint_config').perform(context)

    # Follower arm + cameras
    follower_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare('pai_bringup'),
                    'launch',
                    'so_arm_real_bringup.launch.py',
                ]
            )
        ),
        launch_arguments={
            'usb_port': follower_port,
            'joint_config_file': follower_joint_config,
            'launch_rviz': launch_rviz,
            'use_cameras': use_cameras,
        }.items(),
    )

    # Leader arm teleop
    leader_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare('pai_leader_teleop'),
                    'launch',
                    'leader_bringup.launch.py',
                ]
            )
        ),
        launch_arguments={
            'usb_port': leader_port,
            'joint_config_file': leader_joint_config,
            'description_file': DEFAULT_LEADER_DESCRIPTION,
            'ros2_control_file': DEFAULT_LEADER_ROS2_CONTROL,
            'controllers_file': DEFAULT_LEADER_CONTROLLERS,
            'launch_rviz': 'false',
        }.items(),
    )

    # Episode recorder
    recorder_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare('rosetta'),
                    'launch',
                    'episode_recorder_launch.py',
                ]
            )
        ),
        launch_arguments={
            'contract_path': contract_path,
            'bag_base_dir': bag_base_dir,
        }.items(),
    )

    return [follower_launch, leader_launch, recorder_launch]


def generate_launch_description():
    """Generate launch description with top-level arguments."""
    default_contract = PathJoinSubstitution(
        [
            FindPackageShare('pai_data_collection'),
            'config',
            'rosetta',
            'so_arm101.yaml',
        ]
    )

    declared_arguments = [
        DeclareLaunchArgument(
            'follower_port',
            default_value='/dev/arm_left_follower',
            description='USB port for the follower arm.',
        ),
        DeclareLaunchArgument(
            'leader_port',
            default_value='/dev/arm_left_leader',
            description='USB port for the leader arm.',
        ),
        DeclareLaunchArgument(
            'contract_path',
            default_value=default_contract,
            description='Path to Rosetta contract YAML.',
        ),
        DeclareLaunchArgument(
            'bag_base_dir',
            default_value='datasets/so_arm101/bags',
            description='Output directory for recorded rosbags.',
        ),
        DeclareLaunchArgument(
            'launch_rviz',
            default_value='true',
            description='Launch RViz.',
        ),
        DeclareLaunchArgument(
            'use_cameras',
            default_value='true',
            description='Launch USB cameras.',
        ),
        DeclareLaunchArgument(
            'follower_joint_config',
            default_value='',
            description='Joint calibration YAML for the follower arm.',
        ),
        DeclareLaunchArgument(
            'leader_joint_config',
            default_value='',
            description='Joint calibration YAML for the leader arm.',
        ),
    ]

    return LaunchDescription(
        [
            *declared_arguments,
            OpaqueFunction(function=launch_setup),
        ]
    )
