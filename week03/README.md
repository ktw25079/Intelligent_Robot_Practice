# week03 실습 정리

## 목표

- Python publisher와 subscriber를 `my_first_pkg` 패키지로 구성하고 빌드한다.
- 학번을 적용한 노드·토픽으로 메시지를 송수신하고 rqt_graph에서 연결을 확인한다.

## 과정

### 1. Publisher와 Subscriber 구현

- [talker.py](my_first_pkg/my_first_pkg/talker.py): `chatter`에 1초마다 `hello ros2 N — 이름` 형식의 `String` 메시지를 발행한다. 번호는 0부터 증가하며 이름은 `student_name` 파라미터로 받는다.
- [listener.py](my_first_pkg/my_first_pkg/listener.py): `chatter`를 구독하고 `on_msg()`에서 수신 내용을 출력한다.
- [setup.py](my_first_pkg/setup.py): `console_scripts`에 두 노드의 `main()`을 등록해 `ros2 run my_first_pkg talker`와 `listener`로 실행하게 한다.

### 2. 패키지 배치와 최초 빌드

Ubuntu 22.04와 ROS 2 Humble 환경에서 저장소를 `~/intelligent_robot_practice`에 둔다. 아래 복사는 `~/ire_ws/src/my_first_pkg`가 없는 최초 배치 기준이다. 이미 배치한 경우 해당 패키지를 사용한다.

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions ros-humble-rclpy ros-humble-std-msgs ros-humble-rqt-graph
mkdir -p "$HOME/ire_ws/src"
cp -r "$HOME/intelligent_robot_practice/week03/my_first_pkg" "$HOME/ire_ws/src/"
source /opt/ros/humble/setup.bash
cd "$HOME/ire_ws"
colcon build --packages-select my_first_pkg --symlink-install
source install/setup.bash
```

`--packages-select`는 대상 패키지를 지정하고, `--symlink-install`은 가능한 파일을 심볼릭 링크로 설치한다.

### 3. 노드 실행

[run_pubsub.sh](run_pubsub.sh)는 ROS 2와 `~/ire_ws/install/setup.bash`를 불러오고, `ROS_LOCALHOST_ONLY=1`을 설정한다. 다른 작업공간을 사용했다면 각 터미널에서 `IRE_WS`를 그 경로로 지정한다.

**터미널 1 — 발행:**

```bash
export ROS_DOMAIN_ID=79
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" talker 202302200 강태욱
```

**터미널 2 — 구독:**

```bash
export ROS_DOMAIN_ID=79
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" listener 202302200
```

스크립트가 실행하는 핵심 명령은 다음과 같다. `-r`은 노드·토픽 이름을 변경하고 `-p`는 메시지에 넣을 이름을 지정한다.

```bash
# talker
ros2 run my_first_pkg talker --ros-args \
  -r __node:=talker_202302200 -r chatter:=/chatter_202302200 \
  -p student_name:=강태욱
# listener
ros2 run my_first_pkg listener --ros-args \
  -r __node:=listener_202302200 -r chatter:=/chatter_202302200
```

위 핵심 명령을 직접 사용할 때도 ROS 및 작업공간 환경을 불러오고, 두 터미널의 `ROS_DOMAIN_ID`와 `ROS_LOCALHOST_ONLY`를 맞춘다.

### 4. 연결 확인

두 노드가 실행된 상태에서 **터미널 3**에 입력한다. 스크립트는 `ros2 run rqt_graph rqt_graph`를 실행한다.

```bash
export ROS_DOMAIN_ID=79
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" graph
```

실행을 마치면 각 터미널에서 `Ctrl+C`로 종료한다.

## 결과

talker가 발행한 `hello ros2 N — 강태욱`을 listener가 수신했다. 아래는 시간 정보를 생략한 실제 로그 발췌다.

```text
[talker_202302200]: pub: hello ros2 0 — 강태욱
[listener_202302200]: I heard: hello ros2 0 — 강태욱
```

| Talker: 번호와 이름 발행 | Listener: 같은 번호와 이름 수신 |
| --- | --- |
| ![발행 결과](screenshots/talker_202302200.png) | ![수신 결과](screenshots/listener_202302200.png) |

rqt_graph에서 `/talker_202302200 → /chatter_202302200 → /listener_202302200` 연결을 확인했다. 코드의 기본 노드·토픽 이름에 실행 시 remapping이 적용된 결과다.

![학번을 적용한 노드와 토픽 연결](screenshots/rqt_graph_202302200.png)

[발행 로그](results/talker.log) · [수신 로그](results/listener.log)
