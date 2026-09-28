# week04 실습 정리

## 목표

- turtlesim 거북이가 사각 경로를 반복 주행하도록 구현한다.
- `/start_stop` 서비스로 주행을 정지하고 남은 동작부터 재개한다.
- launch 한 번으로 거북이 시뮬레이터와 순찰 노드를 실행한다.

## 과정

### 1. 코드 구성

ROS 2 패키지는 `mission1_202302200/`에 있다. Ubuntu 22.04, ROS 2 Humble과 turtlesim, colcon이 설치된 환경에서 실행한다.

- [square_motion.py](mission1_202302200/mission1_202302200/square_motion.py): `DRIVE` 직진과 `TURN` 제자리 회전을 반복한다. 이동 거리로 변의 끝을 판단하고 최초 방향을 기준으로 다음 90도 회전 목표를 정한다.
- [patrol.py](mission1_202302200/mission1_202302200/patrol.py): `/turtle1/pose` 수신, `/turtle1/cmd_vel` 속도 발행, `/start_stop` 서비스와 진행 로그를 처리한다. 정지 시 현재 제어 상태를 보존한다.
- [patrol.launch.py](mission1_202302200/launch/patrol.launch.py): turtlesim과 patrol을 함께 실행한다. 기본값은 정지 상태이며 한 변 길이는 3.0 turtlesim 좌표 단위다. 최대 직진 속도는 2.0 좌표 단위/s, 최대 회전 속도는 3.0 rad/s다.
- [test_square_motion.py](mission1_202302200/test/test_square_motion.py): 반복 주행, 회전, 속도 제한, 정지 후 재개를 검증하는 제어기 테스트다.

### 2. 최초 빌드

저장소를 `~/intelligent_robot_practice`에 둔 경우 아래와 같이 `week04`를 작업공간으로 사용한다. ROS 2 Humble 설치 후 필요한 패키지를 준비한다.

```bash
sudo apt update
sudo apt install ros-humble-turtlesim ros-humble-std-srvs python3-colcon-common-extensions
cd ~/intelligent_robot_practice/week04
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select mission1_202302200
```

### 3. 터미널 1: 시뮬레이터와 순찰 노드 실행

```bash
source /opt/ros/humble/setup.bash
source ~/intelligent_robot_practice/week04/install/setup.bash
ros2 launch mission1_202302200 patrol.launch.py
```

기본 turtlesim 초기 상태에서 두 노드가 실행되고 거북이는 시작 요청을 기다린다. 실행 중 reset·teleport·teleop로 위치나 속도를 따로 변경했다면 launch를 다시 실행한다. 시작 후에는 정지 서비스를 호출할 때까지 사각 경로를 반복한다. 종료는 이 터미널에서 `Ctrl+C`를 누른다.

### 4. 터미널 2: 시작·정지·재개

새 터미널에서 환경을 설정한다. 두 터미널의 `ROS_DOMAIN_ID`와 `ROS_LOCALHOST_ONLY` 설정은 같아야 한다.

```bash
source /opt/ros/humble/setup.bash
```

시작 요청:

```bash
ros2 service call /start_stop std_srvs/srv/SetBool "{data: true}"
```

주행 중 정지 요청:

```bash
ros2 service call /start_stop std_srvs/srv/SetBool "{data: false}"
```

남은 동작부터 재개:

```bash
ros2 service call /start_stop std_srvs/srv/SetBool "{data: true}"
```

시연에서는 시작 → 직진 중 정지 → 재개 → 회전 중 정지 → 재개 순서로 확인한다.

### 5. 자동 시연 검증

기존 launch를 종료하고 터미널 1에서 새로 실행한 뒤, 터미널 2에서 `week04`로 이동한다. 아래 명령은 `results/`의 서비스 로그와 검증 JSON을 새 실행 결과로 덮어쓰므로, 기존 결과를 보관하려면 먼저 별도로 복사한다.
수동 서비스 호출 대신 시작·정지 순서를 자동으로 진행하고, 두 바퀴 후 정지하며 검증 JSON을 저장한다.

```bash
cd ~/intelligent_robot_practice/week04
source /opt/ros/humble/setup.bash
python3 -u scripts/verify_patrol.py | tee results/patrol_demo_services.log
```

## 결과

turtlesim 시뮬레이터에서 실행하고 SimpleScreenRecorder로 터미널 2개와 turtlesim 창을 함께 녹화했다.
시작 → 직진 중 정지·재개 → 회전 중 정지·재개 → 사각형 두 바퀴 완료 → 최종 정지를 확인했다.
`Lap 1 complete`, `Lap 2 complete` 로그가 출력되었고, 저장된 정지 전후 측정값에서 위치 변화는 0.0 turtlesim 좌표 단위, 각도 변화는 0.0 rad였다.
두 바퀴에서 자동 종료하는 코드는 없으며, 시연 클라이언트가 최종 정지 서비스를 호출했다.
각 정지 검증은 서비스 응답 후 0.4초를 기다린 뒤 2초 동안 위치·각도를 비교했다.

자료 다운로드: [소스코드 ZIP](results/mission1_202302200.zip?raw=true) · [시연 녹화 MKV](results/patrol_demo_2laps.mkv?raw=true).
ZIP에는 `mission1_202302200/`의 소스, 패키지 설정, launch 파일, 테스트와 실행 안내를 포함했으며 자동 생성 파일은 제외했다.
압축을 풀어 `mission1_202302200/`을 ROS 2 작업공간에 배치한 뒤 위 순서로 빌드한다.

- [시연 영상](results/patrol_demo_2laps.mkv): 2560×1600, 설정 30 fps, 약 49초, 무음.
- [순찰 실행 로그](results/patrol_demo_launch.log): 모서리 회전, 두 바퀴 완료와 최종 정지.
- [서비스 응답 로그](results/patrol_demo_services.log): `SetBool` 시작·정지 요청과 응답. 녹화에서는 [검증 클라이언트](scripts/verify_patrol.py)로 호출 순서를 자동화했다.
- [정지 검증값](results/patrol_demo_verification.json): 직진·회전·최종 정지 전후의 `/turtle1/pose` 값.

![두 바퀴 완료 후 정지한 화면](screenshots/patrol_demo_stopped.png)

왼쪽 위는 순찰 노드의 두 바퀴 완료 로그, 왼쪽 아래는 서비스 응답, 오른쪽은 사각형 궤적과 정지한 거북이다.

제어기 수치 시험은 ROS 없이 반복 주행·각도 경계·속도 제한과 직진 중 재개를 검사하는 2개 테스트로 구성된다. ROS 서비스 정지·재개 결과는 위 로그와 JSON에서 확인한다. 수치 시험은 `week04/`에서 다음과 같이 실행한다.

```bash
PYTHONPATH=mission1_202302200 python3 -m unittest discover -s mission1_202302200/test -v
```
