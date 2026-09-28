# week02 실습 정리

## 목표

- ROS 2 기본 talker와 listener를 실행해 `/chatter` 토픽의 메시지 발행·구독을 확인한다.
- 같은 동작의 Python 코드에서 발행자, 구독자와 타이머의 역할을 이해한다.

## 과정

### 1. 실행 환경 준비

Ubuntu 22.04에 ROS 2 Humble이 설치되어 있어야 한다. 저장소 위치는 `~/intelligent_robot_practice`를 기준으로 한다. 필요한 패키지를 설치한다.

```bash
sudo apt update
sudo apt install ros-humble-demo-nodes-cpp ros-humble-demo-nodes-py ros-humble-rclpy ros-humble-std-msgs
```

### 2. 기본 데모 실행

[run_demo.sh](run_demo.sh)는 ROS 환경을 불러오고 `ROS_LOCALHOST_ONLY=1`로 같은 PC에서 통신하도록 설정한다. talker는 `ros2 run demo_nodes_cpp talker`, listener는 `ros2 run demo_nodes_py listener`로 실행한다.

**터미널 1 — 발행:**

```bash
export ROS_DOMAIN_ID=79
bash "$HOME/intelligent_robot_practice/week02/run_demo.sh" talker
```

**터미널 2 — 구독:**

```bash
export ROS_DOMAIN_ID=79
bash "$HOME/intelligent_robot_practice/week02/run_demo.sh" listener
```

두 터미널의 `ROS_DOMAIN_ID`는 같아야 한다. 여기서는 저장된 로그와 같은 값인 79를 사용한다.

### 3. Python 코드 이해 및 실행

- [talker.py](talker.py): `create_publisher()`로 `chatter`의 `String` 발행자를 만들고, 1초 주기의 타이머에서 `Hello World: N`을 보낸다. 번호는 1부터 증가한다.
- [listener.py](listener.py): `create_subscription()`으로 같은 토픽을 구독하고 `receive_message()`에서 받은 내용을 출력한다.
- 두 파일의 `rclpy.spin()`은 타이머와 메시지 수신을 계속 처리한다. 패키지 빌드 없이 직접 실행한다.

기본 데모를 각 터미널에서 `Ctrl+C`로 종료한 뒤 실행한다.

**터미널 1 — Python 발행자:**

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=79 ROS_LOCALHOST_ONLY=1
python3 "$HOME/intelligent_robot_practice/week02/talker.py"
```

**터미널 2 — Python 구독자:**

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=79 ROS_LOCALHOST_ONLY=1
python3 "$HOME/intelligent_robot_practice/week02/listener.py"
```

## 결과

저장된 기본 데모 로그에서 talker의 `Hello World: N`을 listener가 같은 번호로 수신한 것을 확인했다. 아래는 시간 정보를 생략한 실제 로그 발췌다.

```text
[talker]: Publishing: 'Hello World: 1'
[listener]: I heard: [Hello World: 1]
```

통신 구조는 `/talker → /chatter → /listener`이다. 저장된 로그와 캡처는 기본 데모 실행 자료이며, 별도 Python 파일의 실행 결과는 포함하지 않는다.

| Talker: 번호가 증가하는 메시지 발행 | Listener: 같은 메시지 수신 |
| --- | --- |
| ![발행 결과](screenshots/talker_202302200.png) | ![수신 결과](screenshots/listener_202302200.png) |

[발행 로그](results/talker.log) · [수신 로그](results/listener.log)
