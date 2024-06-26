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

from distutils.spawn import spawn
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, LocalSubstitution, PathJoinSubstitution
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration, PythonExpression
import subprocess
import shlex
import yaml


def convert_to_robot_config(config):
        
        
    package_name = config['package_name']
    
    model_path = os.path.join(get_package_share_directory(
        package_name), config['model_path'])
    
    xml = open(model_path, 'r').read()

    #xml = xml.replace('"', '\\"')

    initial_pose = config['initial_pose']

    robot_namespace = config['robot_namespace']

    return {'name': config['name'], 'robot_namespace': robot_namespace, 'xml': xml, 'initial_pose':initial_pose}

def yaml_parser(yaml_file):
   

    with open(yaml_file) as f:

        robots = yaml.load(f, Loader =yaml.loader.SafeLoader)

    ret_vals = []

    for robot in robots:
        ret_vals.append(convert_to_robot_config(robot))
            
    return ret_vals


def config_to_service_caller(spawns):
    vals = []
    for spawn in spawns:
        service_call = ExecuteProcess(cmd=['ros2', 'service', 'call', '/spawn_entity','gazebo_msgs/SpawnEntity', str(spawn)], output='log')
        vals.append(service_call)
    return vals

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

def service_caller(context, *args, **kwargs):
    print(kwargs)
    robots_to_spawn = LaunchConfiguration("robots_to_spawn")
    return config_to_service_caller(yaml_parser(robots_to_spawn.perform(context=context)))



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
    rviz_arg = DeclareLaunchArgument('rviz', default_value='true',
                              description='Open RViz.')

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

    #Getting CFG
    
    cfg_0 = os.path.join(pkg_skid_gazebo, 'cfg', 'three_robot.yaml')
 
    robots_to_spawn_arg = DeclareLaunchArgument('robots_to_spawn', default_value=cfg_0, description='Absolute Path to YAML File')


    return LaunchDescription([
        DeclareLaunchArgument(
          'world',
          default_value=[os.path.join(pkg_skid_gazebo, 'worlds', 'skid_steer_empty.world'), ''],
          description='SDF world file'),
        robots_to_spawn_arg,
        rviz_arg,
        gazebo,
        rviz,
        rqt,
        rqt_reconfig
    ] + [OpaqueFunction(function=service_caller)]
)
