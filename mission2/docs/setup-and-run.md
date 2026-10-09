# 환경 구성, 최초 빌드와 실행

[미션 2로 돌아가기](../README.md)

## 1. 수행 순서와 재현 범위

수행 순서는 `노트북 Wi-Fi·IP 설정 → Pi 접속 환경 구성 → Ubuntu/ROS/펌웨어 준비 → 패키지 빌드 → bringup → Servo → teleop → 결과 확인`이다. 초기 환경 전환은 수행자 설명에 근거하며, 보존된 설치·빌드 스크립트와 실행 코드를 아래에 연결한다.

아래 명령은 팀 소스를 같은 구조로 배치해 재현하는 절차다. 설치·빌드 스크립트 발췌와 새 PC용 절차를 구분했다. 기존 작업공간이 있다면 복사 전에 내용을 비교한다.

전제: Ubuntu 22.04, ROS 2 Humble의 패키지 저장소 및 ROS 환경, `git`, `colcon`, `rosdep`을 준비한 상태다. PC는 desktop/MoveIt 환경, Pi는 ros-base와 하드웨어 드라이버를 사용한다. OpenCR은 TurtleBot3 Manipulation용 펌웨어가 준비되어 있어야 한다. 보존본의 `.ino`는 참조 파일이며 단독 업로드 프로젝트가 아니다.

## 2. 네트워크 설정

| 장치 | 주소 | 비고 |
| --- | --- | --- |
| 본인 노트북 | `192.168.0.204/24` | 사용자가 확인한 주소 |
| 라즈베리파이 | `192.168.0.21/24` | 실제 SSH 스크립트와 사용자 설명 일치 |
| 게이트웨이 | `192.168.0.1` | 제공 강의 설정 예시 기준, 현장 네트워크에서 확인 |
| DNS | `8.8.8.8` | 제공 강의 설정 예시 기준 |

노트북의 Ubuntu 네트워크 설정에서 실습 Wi-Fi에 연결하고 IPv4 수동 주소·넷마스크·게이트웨이를 지정한다. 팀원 PC에는 중복되지 않는 별도 주소를 사용한다.

Pi에 접속할 수 없는 초기 상태에서는 전원을 종료한 후 SD카드를 노트북에 연결하여 Netplan 파일을 수정하는 방법을 사용한다. 제공 보조자료는 `lsblk -f`로 루트 파티션을 찾고, 해당 파티션의 `etc/netplan/` 파일을 편집한 뒤 안전하게 분리하는 순서를 안내한다. 다음은 **실제 설정 파일 원본이 아닌 팀 주소를 반영한 예시**다. SSID와 비밀번호는 현장 값으로 입력하며 저장소에는 넣지 않는다.

```yaml
network:
  version: 2
  renderer: networkd
  wifis:
    wlan0:
      dhcp4: false
      optional: true
      addresses: [192.168.0.21/24]
      routes:
        - to: default
          via: 192.168.0.1
      nameservers:
        addresses: [8.8.8.8]
      access-points:
        "<실습 Wi-Fi SSID>":
          password: "<현장 비밀번호>"
```

Pi 부팅 후 노트북에서 연결을 확인한다.

```bash
ping -c 4 192.168.0.21
ssh ubuntu@192.168.0.21
```

SSH 성공과 ROS 2 노드 검색 성공은 별도 확인 항목이다. PC와 Pi 양쪽에서 `ROS_DOMAIN_ID=4`, `ROS_LOCALHOST_ONLY=0`을 설정한다.

## 3. 작업공간을 각 컴퓨터에 배치

각 장치에 저장소를 받은 뒤 기준 변수를 지정한다. 아래 복사 명령은 대상 작업공간이 없는 새 환경을 전제로 한다. PC와 Pi의 설치 결과는 서로 복사하지 않고 각 장치에서 빌드한다.

```bash
# PC와 Pi 각각: 저장소 위치가 다르면 REPO만 변경
REPO="$HOME/intelligent_robot_practice"
SNAPSHOT="$REPO/mission2/workspaces"
```

Pi:

```bash
cp -a "$SNAPSHOT/raspberry-pi/home/ubuntu/turtlebot3_ws" "$HOME/"
cp -a "$SNAPSHOT/raspberry-pi/home/ubuntu/lecture05-setup" "$HOME/"
cp -a "$SNAPSHOT/raspberry-pi/home/ubuntu/lecture05-repair_ws" "$HOME/"
```

원본 보정 SDK 링크는 `/home/ubuntu/lecture05-setup/sdk-4.0.3-fixed/ros/dynamixel_sdk`를 가리킨다. Pi 계정이 `ubuntu`이고 위 위치에 배치했다면 원본 링크가 맞는다. 다른 홈에 배치한 경우 **복사한 작업공간 안에서만** 링크를 맞춘다.

```bash
# 기존 항목이 심볼릭 링크인 경우에만 교체
SDK_LINK="$HOME/lecture05-repair_ws/src/dynamixel_sdk"
if [ -L "$SDK_LINK" ]; then
  unlink "$SDK_LINK"
  ln -s "$HOME/lecture05-setup/sdk-4.0.3-fixed/ros/dynamixel_sdk" "$SDK_LINK"
fi
```

원격 PC:

```bash
cp -a "$SNAPSHOT/jetson/home/jetson/ire_ws" "$HOME/"
```

`jetson`은 팀원 PC의 원래 계정 이름이다. 대부분의 스크립트는 현재 계정의 `$HOME/ire_ws`를 사용하며 4분할 UI의 SSH ControlPath만 별도로 맞춰야 한다.

## 4. Pi 의존성 설치와 기본 빌드

[install-pi-packages.sh](../workspaces/raspberry-pi/home/ubuntu/lecture05-setup/install-pi-packages.sh)는 패키지 관리 작업 완료와 `dpkg --audit` 결과를 확인한 뒤 ROS 패키지를 설치하고 `packages.log`에 기록한다. 원본 스크립트의 로그 경로는 `/home/ubuntu/lecture05-setup`이므로 ubuntu 계정의 Pi 배치를 전제로 한다.

```bash
# Pi, ubuntu 계정. ROS 2 apt 저장소가 이미 설정되어 있어야 함
sudo bash ~/lecture05-setup/install-pi-packages.sh
bash ~/lecture05-setup/build-pi-workspace.sh
```

기본 빌드 스크립트는 설치 로그의 `PACKAGE_SETUP_EXIT=0`을 확인한 다음 아래 패키지를 선택해 빌드한다. 앞선 설치가 완료되지 않으면 로그를 기다리므로 순서를 지킨다.

```bash
# build-pi-workspace.sh의 핵심 명령 발췌
source /opt/ros/humble/setup.bash
cd "$HOME/turtlebot3_ws"
export MAKEFLAGS=-j1
colcon build --symlink-install --executor sequential \
  --packages-select turtlebot3_manipulation_description turtlebot3_manipulation_hardware turtlebot3_manipulation_bringup \
  --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
```

`MAKEFLAGS=-j1`과 순차 실행은 Pi에서 빌드 병렬성을 줄이는 설정이다. 자동 생성되는 `build/`, `install/`, `log/`는 보존본에 없다.

## 5. Pi 보정 작업공간 빌드

[CONTENTS.json](../workspaces/CONTENTS.json)의 기록에 해당하는 보정 빌드다. 기본 패키지를 먼저 빌드한 후 수행한다.

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
cd ~/lecture05-repair_ws
MAKEFLAGS=-j1 colcon build --executor sequential \
  --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBUILD_TESTING=OFF
```

보정 작업공간에는 수정한 `dynamixel_sdk`와 `turtlebot3_manipulation_hardware`가 있다. 실행 때 이 환경을 마지막에 source하여 보정본을 사용한다. 빌드 종류와 source 순서는 [작업공간 기록](../workspaces/CONTENTS.json)에 남아 있다.

## 6. 원격 PC 의존성과 빌드

아래는 보존본의 패키지 구성을 바탕으로 정리한 새 PC용 빌드 절차다. Pi 설치 스크립트와 달리 당시 PC의 전체 설치 로그가 남아 있는 것은 아니다. `rosdep`은 시스템에서 초기화된 상태여야 한다.

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install ros-humble-moveit ros-humble-moveit-servo \
  ros-humble-ros2-control ros-humble-ros2-controllers \
  ros-humble-gripper-controllers ros-humble-dynamixel-sdk \
  ros-humble-ros2controlcli python3-colcon-common-extensions python3-rosdep
cd ~/ire_ws
rosdep update
rosdep install --from-paths \
  src/turtlebot3_manipulation/turtlebot3_manipulation_description \
  src/turtlebot3_manipulation/turtlebot3_manipulation_hardware \
  src/turtlebot3_manipulation/turtlebot3_manipulation_bringup \
  src/turtlebot3_manipulation/turtlebot3_manipulation_moveit_config \
  src/turtlebot3_manipulation/turtlebot3_manipulation_teleop \
  --ignore-src --rosdistro humble -r -y
colcon build --symlink-install --packages-up-to turtlebot3_manipulation_teleop
```

이번 미션은 위 teleop 의존 패키지까지 실행한다. 함께 포함된 navigation·Cartographer 패키지는 기반 소스의 참고 구성이다.

## 7. 실행 전 점검

Pi에서 사전 점검을 실행한다. [preflight-robot.py](../workspaces/raspberry-pi/home/ubuntu/lecture05-setup/preflight-robot.py)는 패키지, `/dev/ttyACM0`·`/dev/ttyUSB0`의 읽기·쓰기 권한과 점유 여부, Pi 전원 상태 플래그, OpenCR 모델·모터 연결 플래그를 확인한다.

```bash
bash ~/lecture05-setup/preflight-robot.sh
```

이 스크립트는 통신·패키지 상태를 점검하며 모터 동작과 주변 공간은 검사하지 않는다. 실물 구동 전에는 사람이 팔 주변 공간을 확보하고, 주행은 바닥에서 수행한다.

포트 접근이 실패하면 실제 장치 이름과 권한, udev 설정을 확인한다. 포트를 사용하는 기존 bringup이 있다면 중복 실행하지 않는다. 코드의 검사 결과가 필요할 때는 `~/lecture05-setup/preflight-latest.json`을 확인한다. 이 JSON은 이번 보존본에 포함되어 있지 않다.

## 8. 네 터미널 실행

### 터미널 1 · Pi 하드웨어

```bash
# 원격 PC에서 접속
ssh ubuntu@192.168.0.21
# 이후 명령은 Pi에서 실행
bash ~/lecture05-setup/bringup-robot.sh
```

스크립트는 사전 점검, 세 단계 source, 도메인 설정 후 아래 핵심 명령을 실행한다.

```bash
ros2 launch turtlebot3_manipulation_bringup hardware.launch.py
```

이때 팔이 초기 자세로 움직일 수 있다. 로그는 Pi의 `~/lecture05-setup/bringup-live-fixed.log`에 기록하도록 구현되어 있지만 실제 로그 파일은 이번 보존본에 없다.

### 터미널 2 · 원격 PC의 명령 관찰

```bash
source ~/ire_ws/lecture05-live/robot-env.bash
ros2 topic echo /cmd_vel
```

### 터미널 3 · 원격 PC의 MoveIt Servo

```bash
source ~/ire_ws/lecture05-live/robot-env.bash
ros2 launch turtlebot3_manipulation_moveit_config servo.launch.py use_sim:=false
```

`servo.launch.py`의 기본 `use_sim`은 true이므로 실제 로봇 명령에서 false를 명시한다. 당시 `servo.sh`도 이 값을 명시한다.

### 터미널 4 · 원격 PC의 키보드

```bash
source ~/ire_ws/lecture05-live/robot-env.bash
ros2 run turtlebot3_manipulation_teleop turtlebot3_manipulation_teleop
```

각 PC 터미널마다 환경을 불러온다. 키 입력은 터미널 4에 포커스를 두고 수행한다. 먼저 낮은 속도로 주행·정지를 확인한 다음 관절 키로 팔 형상을 조절한다.

## 9. 상태 확인과 종료

같은 환경을 불러온 별도 PC 터미널에서 확인한다.

```bash
source ~/ire_ws/lecture05-live/robot-env.bash
ros2 node list
ros2 topic list
ros2 control list_controllers
```

또는 `bash ~/ire_ws/lecture05-live/observe.sh`를 사용한다. 실제 결과는 [다섯 컨트롤러 화면](../screenshots/bringup-five-active.png)과 비교한다. 캡처 문구를 새로 실행한 로그처럼 재생성하지 않는다.

종료 시 teleop에서 `Space`로 바퀴 정지 명령을 보낸 후 ESC로 끝낸다. Servo와 bringup을 차례로 종료한다. 하드웨어 코드에는 종료 시 팔 위치 변경과 토크 해제가 있어 팔을 지지하고 주변을 확인한다. 이후 Pi의 운영체제를 종료하고 전원을 정리한다.

```bash
# Pi에서 ROS 프로세스를 종료한 뒤
sudo shutdown -h now
```

## 10. 네 창 자동 배치 스크립트

당시 UI는 Terminator 설정을 사용하는 `x-terminal-emulator` 명령이다. 네 창의 역할과 팀원 계정의 SSH 소켓이 이미 준비된 환경에서 사용했다.

```bash
# 준비 화면만 표시: ROS 실행·로봇 동작을 시작하지 않음
bash ~/ire_ws/lecture05-live/ui/launch-four-pane.sh
```

`--live`를 주면 실제 프로세스를 실행한다. 새 PC에서는 전용 소켓 경로와 tmux 세션이 없을 수 있으므로 먼저 위의 개별 터미널 절차로 동작을 확인한다. 창 배치 자체가 bringup 성공을 증명하는 것은 아니다.
