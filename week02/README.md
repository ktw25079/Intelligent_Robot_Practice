# Week 02 — ROS 2 설치 및 통신 확인

## 목표

ROS 2 Humble 환경에서 talker와 listener를 실행하고,
`/chatter` 토픽을 통한 메시지 발행·구독을 확인한다.

## 과정

### 기본 데모 실행

각각 별도의 터미널에서 실행한다. 스크립트는 ROS 환경을 불러오고,
`demo_nodes_cpp`의 talker와 `demo_nodes_py`의 listener를 실행한다.

```bash
bash "$HOME/intelligent_robot_practice/week02/run_demo.sh" talker
```

```bash
bash "$HOME/intelligent_robot_practice/week02/run_demo.sh" listener
```

### 직접 구현한 Python 코드 실행

기본 데모를 Ctrl+C로 종료한 뒤, [talker.py](talker.py)와
[listener.py](listener.py)를 각각 별도의 터미널에서 실행한다.

```bash
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1
python3 "$HOME/intelligent_robot_practice/week02/talker.py"
```

```bash
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1
python3 "$HOME/intelligent_robot_practice/week02/listener.py"
```

## 결과

기본 데모에서 talker가 발행한 `Hello World: N` 메시지를 listener가
수신하는 것을 확인했다.

```text
/talker → /chatter → /listener

[talker]: Publishing: 'Hello World: 1'
[listener]: I heard: [Hello World: 1]
```

| Talker | Listener |
| --- | --- |
| ![발행 결과](screenshots/talker_202302200.png) | ![수신 결과](screenshots/listener_202302200.png) |

[실습 보고서](실습보고서.odt) · [발행 로그](results/talker.log) · [수신 로그](results/listener.log)
