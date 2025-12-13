from setuptools import find_packages, setup

package_name = 'my_robot_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['my_robot_examples/launch/urdf_launch.py']),
        ('share/' + package_name + '/config',
            ['config/robot_params.yaml']),
        ('share/' + package_name + '/urdf',
            ['urdf/simple_robot.urdf', 'urdf/simple_robot.xacro']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Physical AI Course',
    maintainer_email='info@physical-ai-course.com',
    description='Examples for Physical AI & Humanoid Robotics Course',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'robot_controller = my_robot_examples.robot_controller:main',
            'sensor_processor = my_robot_examples.sensor_processor:main',
            'parameter_node = my_robot_examples.parameter_node:main',
            'talker = my_robot_examples.talker:main',
            'listener = my_robot_examples.listener:main',
            'add_two_ints_server = my_robot_examples.add_two_ints_server:main',
            'add_two_ints_client = my_robot_examples.add_two_ints_client:main',
            'fibonacci_action_server = my_robot_examples.fibonacci_action_server:main',
            'fibonacci_action_client = my_robot_examples.fibonacci_action_client:main',
            'robot_state_publisher_node = my_robot_examples.robot_state_publisher_node:main',
        ],
    },
)