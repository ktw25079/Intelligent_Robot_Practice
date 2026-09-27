# week04 실습 정리

## 목표

- turtlesim 거북이가 사각 경로를 반복 주행하도록 구현한다.
- `/start_stop` 서비스로 주행을 정지하고 남은 동작부터 재개한다.
- launch 한 번으로 거북이 시뮬레이터와 순찰 노드를 실행한다.

## 과정

### 코드 구성

ROS 2 패키지는 `mission1/`에 있다. Ubuntu 22.04, ROS 2 Humble과 turtlesim, colcon이 설치된 환경에서 실행한다.

- [square_motion.py](mission1/mission1_202402312/square_motion.py): `DRIVE` 직진과 `TURN` 제자리 회전을 반복한다. 이동 거리로 변의 끝을 판단하고 최초 방향을 기준으로 다음 90도 회전 목표를 정한다.
- [patrol.py](mission1/mission1_202402312/patrol.py): 위치 수신, 속도 발행, 시작·정지 서비스와 진행 로그를 처리한다. 정지 시 현재 제어 상태를 보존한다.
- [patrol.launch.py](mission1/launch/patrol.launch.py): turtlesim과 patrol을 함께 실행한다. 기본값은 정지 상태이며 한 변 길이는 3.0이다.
- [test_square_motion.py](mission1/test/test_square_motion.py): 반복 주행, 회전, 속도 제한, 정지 후 재개를 검증하는 제어기 테스트다.
- [보고서 초안](report.md): 핵심 코드 발췌, 동작 설명, 결과와 고찰을 정리했다.

### 최초 빌드

저장소를 `~/intelligent_robot_practice`에 둔 경우 아래와 같이 `week04`를 작업공간으로 사용한다.

```bash
cd ~/intelligent_robot_practice/week04
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select mission1_202402312
```

### 터미널 1: 시뮬레이터와 순찰 노드 실행

```bash
source /opt/ros/humble/setup.bash
source ~/intelligent_robot_practice/week04/install/setup.bash
ros2 launch mission1_202402312 patrol.launch.py
```

두 노드가 실행되고 거북이는 시작 요청을 기다린다. 종료는 이 터미널에서 `Ctrl+C`를 누른다.

### 터미널 2: 시작·정지·재개

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

## 결과

SimpleScreenRecorder로 터미널 2개와 turtlesim 창을 함께 녹화했다.
시작 → 직진 중 정지·재개 → 회전 중 정지·재개 → 사각형 두 바퀴 완료 → 최종 정지를 확인했다.
`Lap 1 complete`, `Lap 2 complete` 로그가 출력되었고, 저장된 정지 전후 측정값에서 위치·각도 변화가 모두 0이었다.
두 바퀴에서 자동 종료하는 코드는 없으며, 시연 클라이언트가 최종 정지 서비스를 호출했다.

- [시연 영상](results/patrol_demo_2laps.mkv): 2560×1600, 설정 30 fps, 약 60초, 무음.
- [순찰 실행 로그](results/patrol_demo_launch.log): 모서리 회전, 두 바퀴 완료와 최종 정지.
- [서비스 응답 로그](results/patrol_demo_services.log): `SetBool` 시작·정지 요청과 응답. 녹화에서는 별도 `rclpy` 클라이언트로 호출 순서를 자동화했다.
- [정지 검증값](results/patrol_demo_verification.json): 직진·회전·최종 정지 전후의 `/turtle1/pose` 값.

![두 바퀴 완료 후 정지한 화면](screenshots/patrol_demo_stopped.png)

왼쪽 위는 순찰 노드의 두 바퀴 완료 로그, 왼쪽 아래는 서비스 응답, 오른쪽은 사각형 궤적과 정지한 거북이다.
녹화 시 두 터미널에 `ROS_DOMAIN_ID=44`를 동일하게 설정했고, 거북이 창은 `QT_SCALE_FACTOR=2`로 확대했다.
제어기 테스트 2개가 통과했다. 코드 설명과 고찰은 [보고서 초안](report.md)에 정리했다.
패키지명과 작성자 메타데이터는 제공받은 원본을 유지했으며, 제출 양식과 본인 정보의 일치 여부는 최종 제출 전에 확인해야 한다.
