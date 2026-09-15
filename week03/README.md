# week03 실습 정리

## 목표

`my_first_pkg` 패키지의 publisher와 subscriber를 구현하고,
학번을 적용한 노드·토픽의 메시지 통신을 확인한다.

## 과정

### 1. Publisher와 Subscriber 구현

- [talker.py](my_first_pkg/my_first_pkg/talker.py): `create_publisher()`로 `chatter` 발행자를 만들고, 1초 주기의 타이머에서 `hello ros2 N — 이름` 형식의 `String` 메시지를 보낸다. 이름은 `student_name` 파라미터로 받는다.
- [listener.py](my_first_pkg/my_first_pkg/listener.py): `create_subscription()`으로 `chatter`를 구독하고, 메시지가 도착하면 `on_msg()`에서 내용을 출력한다.
- [setup.py](my_first_pkg/setup.py): `console_scripts`에 `talker`와 `listener`의 `main()`을 등록해 `ros2 run`으로 실행할 수 있게 한다.

### 2. 패키지 빌드

패키지를 `~/ire_ws/src/my_first_pkg`에 준비한 뒤 빌드한다.
`--packages-select`는 빌드할 패키지를 지정하고, `--symlink-install`은 가능한 파일을 복사 대신 심볼릭 링크로 설치한다.

```bash
source /opt/ros/humble/setup.bash
cd "$HOME/ire_ws"
colcon build --packages-select my_first_pkg --symlink-install
```

### 3. 노드 실행 및 연결 확인

각각 별도의 터미널에서 실행한다.
[run_pubsub.sh](run_pubsub.sh)는 ROS 2와 워크스페이스 환경을 불러오고,
노드와 토픽 이름에 학번을 적용한다. talker 명령의 `강태욱`은 메시지에 넣을 이름이다.

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" talker 202302200 강태욱
```

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" listener 202302200
```

두 노드가 실행된 상태에서 rqt_graph를 열어 노드와 토픽의 연결을 확인한다.

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
