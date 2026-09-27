from glob import glob
from setuptools import setup

package_name = 'mission1_202402312'

setup(
    name=package_name,
    version='1.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', 'README.md']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ],
    entry_points={'console_scripts': ['patrol = mission1_202402312.patrol:main']},
)
