#!/usr/bin/env python3
"""
amcl.launch.py
──────────────
AMCL(Adaptive Monte Carlo Localization) 실행 파일
sensor_layer 패키지와 연동

포함 노드:
  1. map_server    — 사전 제작된 지도(.yaml) 로드
  2. amcl          — 파티클 필터 기반 위치 추정
  3. lifecycle_manager — 위 두 노드 생명주기 관리

의존하는 센서 (sensor_layer에서 발행됨):
  - /scan        ← sllidar_ros2 (SLLIDAR T1)
  - /odom        ← tf_manager_cpp/wheel_odom_tf
  - TF: odom → base_link ← wheel_odom_tf

사용법:
  ros2 launch amcl_pkg amcl.launch.py map:=/path/to/map.yaml

시뮬레이터 사용 시:
  ros2 launch amcl_pkg amcl.launch.py map:=/path/to/map.yaml use_sim_time:=true
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    pkg_dir = get_package_share_directory('amcl_pkg')

    # ── Launch 인자 선언 ────────────────────────────────────────────────
    use_sim_time    = LaunchConfiguration('use_sim_time', default='false')
    map_yaml_file   = LaunchConfiguration('map')
    amcl_params     = LaunchConfiguration(
        'amcl_params',
        default=os.path.join(pkg_dir, 'config', 'amcl_params.yaml')
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Gazebo 시뮬레이터 사용 여부'
        ),
        DeclareLaunchArgument(
            'map',
            description='지도 yaml 파일 전체 경로 (필수)'
        ),
        DeclareLaunchArgument(
            'amcl_params',
            default_value=amcl_params,
            description='AMCL 파라미터 yaml 경로'
        ),

        #디버깅용임
        LogInfo(msg='=== AMCL 시작: map_server + amcl + lifecycle_manager ==='),
      

        # ── 1) Map Server ───────────────────────────────────────────────
        Node(
            package='nav2_map_server', #어떤 패키지에서
            executable='map_server', #어떤 프로그램 실행할지
            name='map_server', #ROS2 네트워크에서 부를 이름
            output='screen',  #로그를 터미널에 출력
            parameters=[
                {'use_sim_time': use_sim_time}, #시뮬 시간 사용 여부
                {'yaml_filename': map_yaml_file}, #불러올 지도 경로임,,
            ]
        ),

        # ── 2) AMCL ─────────────────────────────────────────────────────
        # scan_topic  : /scan  (sllidar_ros2가 발행)
        # odom_frame  : odom   (wheel_odom_tf.cpp header.frame_id)
        # base_frame  : base_link (wheel_odom_tf.cpp child_frame_id)
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                amcl_params,
                {'use_sim_time': use_sim_time},
            ]
        ),

        # ── 3) Lifecycle Manager ────────────────────────────────────────
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'autostart': True},
                {'node_names': ['map_server', 'amcl']},
            ]
        ),
    ])
