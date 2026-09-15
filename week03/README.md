# Week 03 — ROS 2 Publisher / Subscriber 실습

- 이름: 강태욱
- 학번: 202302200
- 환경: ROS 2 Humble

## 사용자명 및 홈 경로

현재 로그인 사용자명은 `ktw25079`이며, 홈 디렉터리는 `/home/kangtaeuk`이다.
사용자명만 변경하면 홈 디렉터리 이름은 자동으로 변경되지 않는다.
아래 명령은 `$HOME`을 사용하므로 현재 홈 경로를 따른다.
홈 디렉터리를 `/home/ktw25079`로 이전하고 계정의 홈 경로도 변경하면
같은 명령을 사용할 수 있다. 저장소도 해당 홈 디렉터리 아래에 있어야 한다.

현재 터미널의 사용자명과 홈 경로는 다음 명령으로 확인한다.

```bash
whoami
printenv HOME
```

## 실습 내용

`my_first_pkg`의 talker가 1초마다 `std_msgs/msg/String` 메시지를 발행하고, listener가 메시지를 구독하여 출력한다. 실행 스크립트에서 노드와 토픽 이름에 학번을 붙인다.

```text
/talker_202302200 → /chatter_202302200 → /listener_202302200
```

## 제출 파일

- `my_first_pkg/`: talker, listener 및 패키지 설정
- `run_pubsub.sh`: 학번을 적용하는 실행 스크립트
- `screenshots/rqt_graph_202302200.png`: 노드와 토픽 연결 확인 화면

## 실행 방법

패키지가 `~/ire_ws/src/my_first_pkg`에 있는 기존 실습 환경에서 빌드한다.

```bash
source /opt/ros/humble/setup.bash
cd "$HOME/ire_ws"
colcon build --packages-select my_first_pkg --symlink-install
```

각각 별도의 터미널에서 다음 명령을 실행한다. 스크립트는 ROS 2와 워크스페이스 환경을 자동으로 불러온다.

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" talker 202302200 강태욱
```

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" listener 202302200
```

```bash
bash "$HOME/intelligent_robot_practice/week03/run_pubsub.sh" graph
```

실행 스크립트의 기본 워크스페이스는 `$HOME/ire_ws`이다.
다른 워크스페이스를 사용하는 경우 각 실행 터미널에서 `IRE_WS`를 지정한다.

```bash
export IRE_WS="$HOME/ire_ws"
```

홈 디렉터리를 실제로 이전했다면 기존 `build`와 `install`에 이전 절대 경로가
남을 수 있다. 해당 빌드 결과를 별도로 보관하거나 정리한 뒤 새 위치에서 다시
빌드한다. 사용자명만 변경하고 홈 경로를 유지했다면 경로 변경에 따른 재빌드는
필요하지 않다.

## rqt_graph 결과

아래 캡처에서 talker와 listener가 `/chatter_202302200` 토픽을 통해 연결되어 있음을 확인할 수 있다.

![학번 202302200의 publisher와 subscriber 연결](screenshots/rqt_graph_202302200.png)
