# Week 02 — ROS 2 설치 및 통신 확인

- 이름: 강태욱
- 학번: 202302200
- 환경: Ubuntu 22.04, ROS 2 Humble

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

talker가 `/chatter` 토픽으로 `std_msgs/msg/String` 메시지를 발행하고,
listener가 구독하여 `I heard` 로그를 출력하는지 확인한다.

```text
/talker → /chatter → /listener
```

## 파일 구성

- `실습보고서.odt`: 기존 talker의 Publishing과 listener의 I heard 화면 캡처
- `run_demo.sh`: ROS 2 기본 데모 실행 스크립트
- `talker.py`: 1초마다 `Hello World: N`을 발행하는 직접 구현 코드
- `listener.py`: 수신한 메시지를 출력하는 직접 구현 코드

Python 코드는 보고서의 송수신 동작을 재현하기 위해 추가한 코드이며,
ROS 2 기본 데모 패키지의 원본 소스는 아니다.

## 1. 기본 데모 실행

ROS 2 Humble과 `demo_nodes_cpp`, `demo_nodes_py`가 설치된 환경에서 실행한다.
패키지가 없다면 다음 명령으로 설치한다.

```bash
sudo apt install ros-humble-demo-nodes-cpp ros-humble-demo-nodes-py
```

터미널 두 개를 나란히 열어 각각 실행한다.

```bash
bash "$HOME/intelligent_robot_practice/week02/run_demo.sh" talker
```

```bash
bash "$HOME/intelligent_robot_practice/week02/run_demo.sh" listener
```

스크립트는 ROS 환경을 불러오고, 같은 PC 안에서 통신하도록 설정한다.
내부 실행 명령은 각각 `ros2 run demo_nodes_cpp talker`와
`ros2 run demo_nodes_py listener`이다.

## 2. 직접 구현한 Python 코드 실행

기본 데모를 Ctrl+C로 종료한 뒤 실행한다. 별도의 패키지 빌드 없이 사용할 수 있다.
두 터미널 모두 같은 `ROS_DOMAIN_ID`를 사용해야 한다.
저장소를 다른 위치에 받았다면 아래 경로를 수정한다.

터미널 1:

```bash
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1
python3 "$HOME/intelligent_robot_practice/week02/talker.py"
```

터미널 2:

```bash
source /opt/ros/humble/setup.bash
export ROS_LOCALHOST_ONLY=1
python3 "$HOME/intelligent_robot_practice/week02/listener.py"
```

출력 예시(시간 정보 생략):

```text
[talker]: Publishing: 'Hello World: 1'
[listener]: I heard: [Hello World: 1]
[talker]: Publishing: 'Hello World: 2'
[listener]: I heard: [Hello World: 2]
```

listener를 늦게 실행하면 앞선 메시지는 수신하지 못하므로 번호가 1부터 시작하지
않을 수 있다. 이후 같은 번호의 발행·수신 로그가 나타나면 정상이다.
각 터미널에서 Ctrl+C를 누르면 종료된다.
