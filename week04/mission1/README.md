# Week04 미션 #1 — turtlesim 사각 순찰

조원에게 받은 기존 패키지를 참고하여 AI 도움으로 제어 로직을 재구성한 버전입니다.
패키지명과 Python 모듈명은 `mission1`입니다. 원본 패키지의 작성자 메타데이터는 유지했습니다.

## 실습 요구조건과 구현

- 사각 경로 반복 주행, 궤적에 네 모서리 표시: 직진과 제자리 90도 회전을 반복합니다.
- `/start_stop` (`std_srvs/srv/SetBool`): `true`로 시작·재개, `false`로 정지합니다.
- launch 한 번으로 turtlesim과 순찰 노드를 함께 실행합니다.

## 제어 방식

기존 코드는 네 목표 좌표까지의 거리와 방위각을 계속 계산했습니다.
변경한 코드는 `DRIVE`와 `TURN` 두 상태를 사용합니다.

1. 첫 pose의 위치와 방향을 출발 기준으로 저장합니다.
2. `DRIVE`: 현재 변의 시작점에서 진행 방향으로 이동한 거리를 계산합니다.
   한 변의 길이에 가까워지면 감속하며, 방향 오차를 보정합니다.
3. 한 변을 마치면 직진 속도를 0으로 만들고 `TURN`으로 바꿉니다.
4. `TURN`: 최초 방향을 기준으로 다음 90도 방향까지 제자리 회전합니다.
   현재 각도에 계속 90도를 더하지 않으므로 회전 목표의 누적 오차를 줄입니다.
5. 회전을 마치면 다음 변의 출발 위치를 저장합니다. 네 번째 회전 후 한 바퀴를 기록합니다.

서비스로 정지해도 현재 변의 시작점과 제어 상태는 보존합니다.
따라서 직진 중이든 회전 중이든 남은 동작부터 재개합니다.
pose가 0.5초 이상 들어오지 않으면 속도 0을 발행하며, 수신이 복구되면 이어갑니다.
출발 pose가 없거나 예상 사각형이 화면을 벗어나면 시작 요청을 실패 처리합니다.

- `mission1/square_motion.py`: 거리·각도 계산과 상태 전환
- `mission1/patrol.py`: ROS 토픽, 서비스, 타이머, 진행 로그
- `launch/patrol.launch.py`: 두 노드 동시 실행과 실행 인자
- `test/test_square_motion.py`: 세 바퀴 반복, 회전 각도 경계, 속도 제한, 중간 재개 검증

## 빌드 및 실행 (ROS 2 Humble)

패키지 폴더를 포함하는 작업공간에서:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select mission1
source install/setup.bash
ros2 launch mission1 patrol.launch.py
```

처음에는 정지 상태입니다. 다른 터미널에서:

```bash
source /opt/ros/humble/setup.bash
ros2 service call /start_stop std_srvs/srv/SetBool "{data: true}"
ros2 service call /start_stop std_srvs/srv/SetBool "{data: false}"
```

실행 인자로 설정을 바꿀 수 있습니다.

```bash
ros2 launch mission1 patrol.launch.py side_length:=2.5 speed:=1.5 turn_speed:=2.0 autostart:=true
```

파라미터는 시작 시 읽습니다. 변경값을 제어에 적용하려면 launch를 재실행하세요.
다른 터미널에서 서비스를 호출할 때 ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY는 같아야 합니다.
`Ctrl+C`로 종료합니다.

## 검증

작업공간에서 제어기 검증:

```bash
PYTHONPATH=mission1 python3 -m unittest discover -s mission1/test -v
```

시연에서는 시작 → 직진 중 정지 → 재개 → 회전 중 정지 → 재개 → 두 바퀴 반복을 확인하세요.
직진 중 정지하면 위치가, 회전 중 정지하면 각도가 유지되어야 합니다.

## 제한 및 제출

기본 turtlesim 환경에서 순찰 노드만 거북이를 제어하는 것을 전제로 합니다.
주행 중 reset, teleport 또는 별도 teleop를 사용했다면 launch를 재시작하세요.
거리·각도 허용 오차와 시뮬레이터의 이산 갱신 때문에 여러 바퀴 후 궤적이 조금 어긋날 수 있습니다.

제출물은 패키지 소스 압축, SimpleScreenRecorder 시연 녹화, 코드·캡처를 활용한 보고서입니다.
`build/`, `install/`, `log/`, `__pycache__/`는 제출물에 포함하지 않습니다.
