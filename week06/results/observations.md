# 실행 확인 기록

2026-10-12, Ubuntu 22.04 / ROS 2 Humble / Gazebo Classic 11.10.2.

- `turtlebot3_simulations` humble 커밋: `a35a56c8b04877dc89772b598084d8ce648a9023`.
- 공식 `turtlebot3_manipulation_gazebo/gazebo.launch.py`로 `turtlebot3_manipulation_system` 생성 성공: [spawn.log](spawn.log).
- `/scan`: `sensor_msgs/msg/LaserScan`, 발행자 1개와 구독자 1개: [scan-info.txt](scan-info.txt). 이 조회는 발행 주기 측정이 아니다.
- `joint_state_broadcaster`, `arm_controller`, `imu_broadcaster`, `gripper_controller`: `active` 확인: [controllers.txt](controllers.txt).
- 바퀴 구동은 Gazebo의 `diff_drive` 플러그인이 담당한다. `/cmd_vel` 구독, `/odom` 발행, `odom → base_footprint` TF 발행은 [gazebo.log](gazebo.log)에서 확인된다. 별도의 diff_drive_controller 활성화를 주장하지 않는다.
- 최종 캡처에는 RViz2 LaserScan의 `Status: Ok`, `/scan`, Size 0.05m, RobotModel, 카메라 영상, Gazebo 월드, RQt Plot의 선속도·각속도 곡선이 보인다.
- 최종 주행 구간은 선속도 0.08m/s 직진, 각속도 0.30rad/s 회전, 정지 명령으로 구성했다. Plot을 일시정지해 기록을 유지했다.
- 주행 도중 로봇 자세가 불안정해져 `/reset_world`로 초기 위치를 복원했다. 원인은 별도 검증하지 않았다. 최종 캡처의 센서 영상은 복원 후 정지 상태이고, Plot은 초기화 전 주행 명령 기록이다.
- 키보드 제어는 `teleop.py`의 베이스 전용 i/k/j/l/Space를 사용했다. MoveIt Servo, 팔 키보드 조작, 사각 경로 도전 과제, 실물 재검증은 수행하지 않았다.
- Topic Monitor에서 `/odom`, `/cmd_vel`을 선택했다. `/cmd_vel`의 약 10Hz 표시는 확인했으나 `/odom`의 GUI 수신 주기는 확인하지 못했다. `/odom` 위치 메시지 수신은 별도로 ROS 2 CLI에서 확인했다.

## 실행 환경과 로그 해석

캡처 당시 Gazebo와 추가 의존성은 관리자 설치 대신 작업 폴더에 압축 해제했고, ament 리소스 경로를 등록하여 공식 launch·URDF·mesh를 사용했다. 저장소의 `env.sh`는 일반적인 apt 설치 및 colcon 작업공간을 사용하도록 정리한 실행 안내이며, 기존 폴더에 의존하는 설치 바이너리는 포함하지 않는다. `mission.launch.py`와 `teleop.py`의 동작은 캡처 당시 코드와 동일하다.

`gazebo.log`는 실제 원본 로그이다. 이미 활성화된 joint_state_broadcaster에 대한 중복 구성 오류가 한 번 포함되어 있으며, 이후 서비스 조회에서 최종 active 상태를 확인했다. battery 센서 생략 및 arm_controller의 deprecated 파라미터 경고도 포함된다. 무오류 실행이라고 해석하지 않는다.

## 정리본 검증

공개용 launch·teleop 파일은 실제 실행본과 바이트 단위로 일치한다. Python 문법, 셸 문법, RViz YAML, 변경 문서의 상대 링크, 기존 실행 환경에서의 launch 인자 해석을 확인했다. 캡처 SHA-256은 `76f9a0ef1de07bf6c5f6e4d8286c1e6ed225d53fc2e11431138577c22300c5b9`이다. 일반 apt 설치 및 colcon 작업공간용 env.sh는 별도 환경에서 실행하지 않았으며 문법과 소스 경로 구성을 확인했다.
