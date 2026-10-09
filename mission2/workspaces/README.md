# 미션 2 실제 작업공간

팀원이 제공한 `lecture05-actual-workspaces-20261008`의 Pi·원격 PC 소스다. 실행 스크립트, ROS 패키지와 수정 SDK가 포함된다. 실물 구동 결과는 [미션 결과 폴더](../screenshots/)에서 확인할 수 있다.

## 구조

| 경로 | 역할 |
| --- | --- |
| [raspberry-pi/home/ubuntu/turtlebot3_ws](raspberry-pi/home/ubuntu/turtlebot3_ws/) | Pi 기본 패키지 소스 |
| [raspberry-pi/home/ubuntu/lecture05-repair_ws](raspberry-pi/home/ubuntu/lecture05-repair_ws/) | 수정 하드웨어 드라이버, 보정 SDK를 가리키는 링크 |
| [raspberry-pi/home/ubuntu/lecture05-setup](raspberry-pi/home/ubuntu/lecture05-setup/) | 설치·빌드·사전 점검·bringup 스크립트, SDK 소스 |
| [jetson/home/jetson/ire_ws/src](jetson/home/jetson/ire_ws/src/) | 원격 PC의 ROS 패키지 |
| [jetson/home/jetson/ire_ws/lecture05-live](jetson/home/jetson/ire_ws/lecture05-live/) | Servo·teleop·관찰·4분할 UI 및 진단 소스 |
| [CONTENTS.json](CONTENTS.json) | 원본 작성자가 기록한 범위·버전·환경 순서 |
| [SHA256SUMS](SHA256SUMS) | 이 폴더에 보존한 원본 일반 파일의 SHA-256 |

`SHA256SUMS`는 현재 작업공간의 원본 일반 파일에 대한 해시 목록이다. 안내 문서, 해시 목록 자체와 SDK 심볼릭 링크는 제외한다.

```bash
# 이 README가 있는 workspaces/에서 실행
sha256sum -c SHA256SUMS
```

SDK 링크는 `/home/ubuntu/lecture05-setup/sdk-4.0.3-fixed/ros/dynamixel_sdk`를 가리키며 이 GitHub 트리에서는 일반 파일처럼 열 수 없다. 링크 대상 소스는 [별도 폴더](raspberry-pi/home/ubuntu/lecture05-setup/sdk-4.0.3-fixed/ros/dynamixel_sdk/)에 포함되어 있다. 실제 빌드 때는 [배치 안내](../docs/setup-and-run.md)를 따른다.

## 기반 소스와 실행 범위

- TurtleBot3 Manipulation 기반 소스: ROBOTIS, 원본 기록의 커밋 `814f140e8e208994dd6159f189993156e3943d98`.
- 보정 DynamixelSDK 기반 버전: 원본 기록상 `4.0.3`.
- ROBOTIS 라이선스와 각 파일의 저작권 표시를 보존했다. [Manipulation 라이선스](jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/LICENSE), [보정 SDK 라이선스](raspberry-pi/home/ubuntu/lecture05-setup/sdk-4.0.3-fixed/LICENSE).
- ROBOTIS 기반 소스에 팀 실행 스크립트와 통신 보정을 함께 사용했다.
- `build/`, `install/`, `log/`, SSH 인증정보와 소켓, 실제 업로드한 펌웨어 바이너리·툴체인은 없다.
- `diagnostics/`는 문제 조사용 코드다. 해당 진단의 실행 결과 로그는 포함되어 있지 않다.
- navigation·Cartographer·Gazebo 파일은 기반 패키지의 참고 구성이다. 이번 미션의 실행 범위는 하드웨어 bringup, Servo와 teleop이다.

패키지 내부의 기존 README는 원본 참고자료이고, 이번 팀 환경의 실행 순서는 [미션 실행 문서](../docs/setup-and-run.md)를 기준으로 한다.
