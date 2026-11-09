# Pi CSI 카메라 실행과 재생

[week08 실습 정리](../README.md)

### 1. 카메라 연결과 실행 코드

Ubuntu 22.04·ROS 2 Humble PC와 Raspberry Pi를 `ROS_DOMAIN_ID=4`로 연결했다. 정상 동작하던 조의 IMX219 카메라를 장착한 뒤 320×240 영상 수신을 확인했다. 아이패드에 `DICT_4X4_50`의 ID 0 마커를 띄우고, 검은 사각형 한 변을 약 13cm로 측정해 `marker_size=0.13`을 적용했다.

실행 코드는 [강의 저장소의 8주차 예제](https://github.com/iCIRLab/icir_ire_lecture/tree/master/ire_week08_vision)를 가져와 실물 토픽으로 실행했다. 직접 새 검출 알고리즘을 작성한 것은 아니다. 패키지에 ArUco 실행 진입점, `geometry_msgs` 의존성, 보정·RViz 설정 설치를 반영했다.

| 파일 | 역할 |
| --- | --- |
| [aruco_detect.py](../ire_week08_vision/ire_week08_vision/aruco_detect.py) | 영상·CameraInfo 구독 → ID 검출 → pose 및 표시 영상 발행 |
| [color_detect.py](../ire_week08_vision/ire_week08_vision/color_detect.py) | HSV 빨강 검출, `/red_pillar/exists` 발행 |
| [generate_aruco.py](../ire_week08_vision/ire_week08_vision/generate_aruco.py) | 흰 여백을 포함한 ID 0~9 마커 생성 |
| [보정 파일](../ire_week08_vision/config/pi_camera_320x240.yaml) | 강의 제공 320×240 카메라 행렬·왜곡계수 |
| [RViz 설정](../ire_week08_vision/config/vision_lab.rviz) | `base_footprint` 기준 검출 영상·pose 좌표축 표시 |
| [check_topics.py](../scripts/check_topics.py) | 정해진 시간 동안 영상·보정·pose 수신 수와 검출 ID 저장 |
| [ID 0 마커](../markers/aruco_0.png) | 아이패드 표시용 이미지 |

### 2. PC 패키지 준비

아래는 일반 설치 환경에서의 재현 명령이다. 저장소를 `~/intelligent_robot_practice`에 받은 상태로 실행한다. 패키지에는 실물 카메라 예제만 포함하며 Gazebo 월드는 포함하지 않는다.

```bash
sudo apt install python3-opencv python3-numpy python3-colcon-common-extensions \
  ros-humble-cv-bridge ros-humble-geometry-msgs ros-humble-rviz2 ros-humble-rosbag2
source /opt/ros/humble/setup.bash
cd ~/intelligent_robot_practice/week08
colcon build --base-paths ire_week08_vision
source install/setup.bash
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
```

실습 당시에는 기존 `camera_ros`·libcamera 설치와 로봇의 TurtleBot3 Manipulation 작업공간을 사용했다. 카메라 설치 자체를 위 PC 패키지가 수행하지는 않는다.

### 3. 로봇 카메라와 PC 검출 실행

PC의 `week08/`에서 보정 파일을 로봇에 복사한다. `<로봇 IP>`는 해당 로봇 주소로 바꾼다.

```bash
ssh ubuntu@<로봇 IP> 'mkdir -p ~/.ros/camera_info'
scp ire_week08_vision/config/pi_camera_320x240.yaml ubuntu@<로봇 IP>:~/.ros/camera_info/
```

**로봇 SSH 터미널 — 카메라:**

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
export LD_LIBRARY_PATH=/usr/local/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
ros2 run camera_ros camera_node --ros-args \
  -p format:=RGB888 -p width:=320 -p height:=240 \
  -p camera_info_url:=file:///home/ubuntu/.ros/camera_info/pi_camera_320x240.yaml
```

**로봇 별도 SSH 터미널 — TF와 하드웨어 브링업:**

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
# 이번 로봇은 이전 실습에서 수정한 하드웨어·SDK overlay도 사용했다.
source ~/lecture05-repair_ws/install/setup.bash
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0 LDS_MODEL=LDS-01
ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
```

이번 실행에서 팔 제어기 초기화는 실패했지만 `robot_state_publisher`는 실행되어 `base_footprint → camera_rgb_optical_frame`의 정적 TF를 확인했다. 팔 정상 구동을 확인한 실습은 아니다.

**PC 터미널 1 — `week08/`에서 검출:**

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
ros2 run ire_week08_vision aruco_detect --ros-args \
  -p image_topic:=/camera/image_raw -p camera_info_topic:=/camera/camera_info \
  -p marker_size:=0.13 -p show_windows:=true
```

**PC 터미널 2 — 같은 환경 설정 후 표시·확인:**

```bash
rviz2 -d ire_week08_vision/config/vision_lab.rviz
# 별도 터미널에서
ros2 topic echo /aruco/pose --once
```

### 4. rosbag 기록과 재생

카메라 실행 중 `/camera/image_raw`와 `/camera/camera_info`를 함께 기록했다. 녹화 명령은 15초 실행했으며, 발견·연결 시간을 제외하고 저장된 메시지 구간은 약 6.125초다.

```bash
# PC의 week08/에서 새 기록 생성; 끝낼 때 Ctrl+C
ros2 bag record /camera/image_raw /camera/camera_info -o results/new_aruco_bag
# 저장된 실습 데이터 재생
ros2 bag play results/aruco_bag --rate 0.5
# 별도 터미널
ros2 topic echo /aruco/pose --once
```

재생 전에 실시간 카메라 발행을 중단해야 입력이 섞이지 않는다. 이번에는 카메라 종료·재실행 시 커널 오류가 있었으므로 로봇의 **카메라 실행 바이너리 PID만** `kill -STOP <PID>`로 일시 정지했다. 5초 동안 영상·보정·pose가 모두 0건임을 확인한 뒤, 검출 노드를 새로 시작해 기존 보정 캐시 없이 재생했다. 검증 후 `kill -CONT <같은 PID>`로 실시간 수신을 복구했다. 이는 카메라 노드를 완전히 종료하는 절차와는 다르다.

로봇 없이 bag만 확인할 때는 실시간 카메라를 실행하지 않고, RViz의 Fixed Frame을 `camera_rgb_optical_frame`으로 바꿀 수 있다. 저장된 화면의 `base_footprint` 표시는 로봇이 제공한 TF를 사용한 결과다.

검증 도구는 `python3 scripts/check_topics.py results/check 20`으로 20초 수신 결과를 저장한다. `check_topics.py`는 실습 환경인 OpenCV 4.5.4 기준이다.
