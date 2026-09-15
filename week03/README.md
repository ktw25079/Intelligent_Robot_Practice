# Week 03 — ROS 2 Publisher / Subscriber 실습

## 목표

`my_first_pkg` 패키지의 publisher와 subscriber를 구현하고,
학번을 적용한 노드·토픽의 메시지 통신을 확인한다.

## 과정

### 패키지 빌드

[talker.py](my_first_pkg/my_first_pkg/talker.py)는 1초마다
`std_msgs/msg/String` 메시지를 발행하고,
[listener.py](my_first_pkg/my_first_pkg/listener.py)는 수신한 메시지를 출력한다.

패키지를 `~/ire_ws/src/my_first_pkg`에 준비한 뒤 빌드한다.

```bash
source /opt/ros/humble/setup.bash
cd "$HOME/ire_ws"
colcon build --packages-select my_first_pkg --symlink-install
```

### 노드 실행 및 연결 확인

각각 별도의 터미널에서 실행한다.
[run_pubsub.sh](run_pubsub.sh)는 ROS 2와 워크스페이스 환경을 불러오고,
노드와 토픽 이름에 학번을 적용한다.

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" talker 202302200 강태욱
```

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" listener 202302200
```

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" graph
```

## 결과

talker가 발행한 `hello ros2 N — 강태욱` 메시지를 listener가 수신하고,
rqt_graph에서 다음 연결을 확인했다.

```text
/talker_202302200 → /chatter_202302200 → /listener_202302200
```

| Talker | Listener |
| --- | --- |
| ![발행 결과](screenshots/talker_202302200.png) | ![수신 결과](screenshots/listener_202302200.png) |

![노드와 토픽 연결](screenshots/rqt_graph_202302200.png)

[발행 로그](results/talker.log) · [수신 로그](results/listener.log)
