from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'ire_week08_vision'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jinseong Park',
    maintainer_email='js.park@cnu.ac.kr',
    description='IRE 8주차 — 색 검출 예제·ArUco 마커 생성·미션 월드',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'aruco_detect = ire_week08_vision.aruco_detect:main',
            'color_detect = ire_week08_vision.color_detect:main',
            'generate_aruco = ire_week08_vision.generate_aruco:main'
        ],
    },
)
