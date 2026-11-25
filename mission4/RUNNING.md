# 실행 환경과 재현

```text
실행 환경과 순서
Ubuntu22.04 / ROS2 Humble / OpenMANIPULATOR-X 장착 TurtleBot3.
시스템 Python3 사용. AI용 conda 환경과 섞지 않는다.
필요: rclpy, sensor_msgs, control_msgs, trajectory_msgs, builtin_interfaces, moveit_msgs, ament_index_python, numpy, scipy, turtlebot3_manipulation_description 및 로봇 bringup/MoveIt 패키지.
기존 로봇 워크스페이스를 설치한 상태에서 필요 시:
sudo apt install python3-numpy python3-scipy ros-humble-moveit-msgs

1. Pi와 PC에서 동일 ROS_DOMAIN_ID(기존 장비는4), ROS_LOCALHOST_ONLY=0 설정.
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
Pi: ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
PC 별도 터미널(같은 환경): ros2 launch turtlebot3_manipulation_moveit_config moveit_core.launch.py
MoveIt Servo 동시 실행 금지. 기존 bringup 중복 실행하지 말 것.

2. 이 폴더의 ros_package/ire_week11_moveit을 별도 워크스페이스 src에 복사.
mkdir -p ~/mission4_recording_ws/src
cp -r ros_package/ire_week11_moveit ~/mission4_recording_ws/src/
cd ~/mission4_recording_ws
colcon build --symlink-install --packages-select ire_week11_moveit
source install/setup.bash
같은 이름의 강의 패키지가 있어 새 패키지는 이 전용 워크스페이스에 두고 마지막으로 source한다.

3. 검사만(모터 명령 없음, 실제 ROS 상태/MoveIt 서비스 연결 필요):
ros2 run ire_week11_moveit pick_demo_202302200
실제 동작(재교시·주변 확보 후):
ros2 run ire_week11_moveit pick_demo_202302200 --execute
직접 실행도 가능: python3 code/pick_demo_202302200.py [--execute]

기존 교시: 5×5×10cm 사각 물체, 상자 면과 그리퍼 면 평행. home=[0,-1.05,1.05,0], gripper=.019.
TEACH_GRASP=[0.06902913545485385,0.7086991240031663,-0.3144660615165564,0.9433981845496693]. B는 joint1 -20도.
다른 로봇/물체/탁자/배치에서는 좌표·높이·충돌 모델 재확인과 재교시 필요. 기존값을 바로 실행하지 않는다.
검사는 정밀한 실물 접촉·마찰 성공을 보장하지 않는다. 필요 시 전원 차단 위치를 확보하고 저속 교시한다.
스크립트 위치의 logs/와 reference/에 새 실행 기록 생성. 기록의 physical_success_confirmed=false는 자동 동작 로그만으로 물체 성공을 판정하지 않는다는 의미.
학번 변경 시 코드 파일명, CMakeLists의 설치 파일명과 실행 파일명, package.xml의 작성자 정보를 함께 변경한다. 원본 실행 증거를 팀원의 실행 결과라고 표시하지 않는다.
```
