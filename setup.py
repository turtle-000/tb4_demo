from setuptools import find_packages, setup

package_name = 'tb4_demo'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Teacher',
    maintainer_email='teacher@example.com',
    description='ROS 2 Jazzy educational package for TurtleBot 4 high school lab',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'drive_simple = tb4_demo.drive_simple:main',
            'mission_drive = tb4_demo.mission_drive:main',
            'lidar_avoid = tb4_demo.lidar_avoid:main',
        ],
    },
)
