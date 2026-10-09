# mission1_202302200 · turtlesim 사각 순찰

## 목표

- 직진과 제자리 90도 회전을 반복하여 사각 경로를 순찰한다.
- `/start_stop` 서비스로 정지하고 남은 동작부터 재개한다.
- launch 한 번으로 turtlesim과 순찰 노드를 실행한다.

## 과정

### 코드 구성과 제어 방식

팀원이 공유한 패키지를 참고하여 거리·방향 기반 제어 로직을 구성했다. ROS 패키지명과 Python 모듈명은 `mission1_202302200`이다.

| 파일 | 역할 |
| --- | --- |
| [square_motion.py](mission1_202302200/square_motion.py) | 이동 거리·방향 오차로 `DRIVE`와 `TURN` 상태 전환 |
| [patrol.py](mission1_202302200/patrol.py) | `/turtle1/pose` 수신, `/turtle1/cmd_vel` 발행, `/start_stop` 서비스 |
| [patrol.launch.py](launch/patrol.launch.py) | turtlesim·patrol 실행과 파라미터 설정 |
| [test_square_motion.py](test/test_square_motion.py) | 반복 주행, 각도 경계, 속도 제한, 직진 중 재개 수치 시험 |

1. 첫 pose의 위치와 방향을 출발 기준으로 저장한다.
2. `DRIVE`에서 변의 시작점부터 진행 방향으로 이동한 거리를 계산한다. 끝에 가까워지면 감속하고 방향 오차를 보정한다.
3. 한 변을 마치면 직진 속도를 0으로 하고 `TURN`으로 전환한다.
4. 최초 방향을 기준으로 다음 90도 목표까지 제자리 회전한다. 회전 후 다음 변의 기준점을 저장하고 네 번째 회전이 끝나면 한 바퀴를 기록한다.

정지 중에는 현재 변의 기준점과 제어 상태를 유지한다. pose 수신이 0.5초를 넘겨 끊기면 속도 0을 발행하고, 수신이 복구되면 이어간다. 시작 요청에는 최신 pose와 화면 안에 들어오는 사각 경로가 필요하다.

### 최초 빌드와 실행

Ubuntu 22.04와 ROS 2 Humble 환경에서 패키지 폴더를 ROS 2 작업공간에 둔다. 저장소의 `mission1/` 또는 이 패키지를 배치한 작업공간에서 실행한다.

```bash
sudo apt update
sudo apt install ros-humble-turtlesim ros-humble-std-srvs python3-colcon-common-extensions
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select mission1_202302200
source install/setup.bash
ros2 launch mission1_202302200 patrol.launch.py
```

처음에는 정지 상태다. 다른 터미널에서 같은 `ROS_DOMAIN_ID`와 `ROS_LOCALHOST_ONLY` 설정으로 서비스를 호출한다.

```bash
source /opt/ros/humble/setup.bash
# 시작 또는 재개
ros2 service call /start_stop std_srvs/srv/SetBool "{data: true}"
# 정지
ros2 service call /start_stop std_srvs/srv/SetBool "{data: false}"
```

| 실행 인자 | 기본값 | 의미 |
| --- | --- | --- |
| `side_length` | 3.0 | 한 변의 길이, turtlesim 좌표 단위 |
| `speed` | 2.0 | 최대 직진 속도, 좌표 단위/s |
| `turn_speed` | 3.0 | 최대 회전 속도, rad/s |
| `autostart` | false | 서비스 요청 없이 시작할지 여부 |

파라미터는 시작 시 읽는다. 다음은 기본값과 다른 설정으로 실행하는 예시다.

```bash
ros2 launch mission1_202302200 patrol.launch.py side_length:=2.5 speed:=1.5 turn_speed:=2.0 autostart:=true
```

기본 turtlesim 환경에서 순찰 노드가 거북이를 단독 제어한다. 실행 중 reset·teleport·별도 teleop를 사용했다면 launch를 재시작한다. 종료는 launch 터미널에서 `Ctrl+C`로 수행한다.

## 결과

저장된 시뮬레이터 시연에서 시작 → 직진 중 정지·재개 → 회전 중 정지·재개 → 두 바퀴 완료 → 최종 정지를 확인했다. 검증 클라이언트가 두 바퀴 후 정지 서비스를 호출했으며 순찰 노드 자체는 정지 요청 전까지 반복한다. 각 정지 후 0.4초를 기다린 뒤 2초간 비교한 위치·각도 변화는 모두 0이었다.

별도의 수치 시험 2개는 ROS 없이 세 바퀴 반복, 각도 경계, 속도 제한과 직진 중 재개를 확인한다. 패키지를 포함한 작업공간에서 실행한다.

```bash
PYTHONPATH=mission1_202302200 python3 -m unittest discover -s mission1_202302200/test -v
```

수치 시험과 실제 ROS 서비스 시연은 별도 검증이다. 거리·각도 허용 오차와 시뮬레이터 갱신 간격으로 반복 궤적에는 작은 편차가 생길 수 있다.
