from setuptools import find_packages, setup

package_name = 'physical_ai_examples'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'talker = physical_ai_examples.publisher_member_function:main',
            'listener = physical_ai_examples.subscriber_member_function:main',
        ],
    },
)