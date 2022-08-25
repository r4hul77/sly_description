# Copyright 2019 Louise Poubel
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

"""Launch Gazebo with a world that has Dolly, as well as the follow node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import subprocess
import shlex


def source_file(path):
    command = shlex.split("env -i bash -c 'source '"+path+"' && env'")
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = list(map(lambda x: x.decode(), line.partition(b'=')))
        value = value.strip("\n")
        if(key in os.environ):
            os.environ[key] = ":".join([value, os.environ[key]])
        else:
            os.environ[key] = value
        print(f"{key} : {os.environ[key]}")
    proc.communicate()


def generate_launch_description():
    source_file('/usr/share/gazebo/setup.bash')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_skid_gazebo = get_package_share_directory('sly_description')

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )


    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=[],
    )

    # RQT
    rqt_reconfig = Node(
        package='rqt_reconfigure',
        executable='rqt_reconfigure',
        arguments=[]
    )

    rqt = Node(
        package="rqt_console",
        executable="rqt_console",
        arguments=[]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
          'world',
          default_value=[os.path.join(pkg_skid_gazebo, 'worlds', 'skid_steer_empty.world'), ''],
          description='SDF world file'),
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Open RViz.'),
        gazebo,
        rviz,
        rqt,
        rqt_reconfig
    ])
