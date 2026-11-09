# 재현 환경과 실행 순서

[저장소 첫 화면](../README.md) · [검증 근거](EVIDENCE.md)

기준 환경은 Ubuntu 22.04와 ROS 2 Humble이다. 실습별 패키지·추가 의존성은 해당 README에서 설치한다. 전체 저장소를 한 작업공간으로 빌드하지 않고 아래 단위를 사용한다.

## 실행 단위

| 실습 | 실행 위치·빌드 | ROS 환경 | 장치 |
| --- | --- | --- | --- |
| [week02](../week02/README.md) | 빌드 없이 `run_demo.sh` 또는 Python | domain 79, localhost 1 | PC |
| [week03](../week03/README.md) | `~/ire_ws`의 `my_first_pkg`만 빌드 | domain 79, localhost 1 | PC |
| [Mission 1](../mission1/README.md) | `mission1/`에서 해당 패키지 빌드 | 같은 domain, localhost 1 권장 | PC / turtlesim |
| [Mission 2](../mission2/docs/setup-and-run.md) | PC·Pi 각각 보존 소스 배치 후 빌드 | domain 4, localhost 0 | PC + Pi + OpenCR |
| [week06](../week06/README.md) | `~/tb3_sim_ws`의 시뮬레이션 패키지 빌드 | domain 66, localhost 1, sim time | PC / Gazebo |
| [week07](../week07/README.md) | 별도 빌드 없이 URDF launch | 같은 domain, localhost 1 권장 | PC / RViz |
| [week08](../week08/docs/pi-camera-workflow.md) | `week08/`에서 영상 패키지 빌드 | domain 4, localhost 0 | Pi 카메라 + PC |
| [week09](../week09/README.md) | `week09/scripts/build.sh`로 지정 5개 빌드 | domain 4, localhost 0, wall time | PC + 실물 로봇 |

`ROS_DOMAIN_ID`는 실습 장비의 실제 그룹과 맞춘다. 다른 도메인으로 실행한 ros2 daemon의 결과가 남아 있으면 올바른 환경을 source한 뒤 `ros2 daemon stop`으로 재탐색한다. 다른 실습의 overlay를 한 터미널에 계속 겹쳐 source하지 않고 새 터미널에서 시작한다.

## 현재 실물 네트워크

현재 운용은 휴대폰 핫스팟을 사용한다. Mission 2의 `192.168.0.*`와 공유기 설정은 당시 기록이며 현재 접속 주소가 아니다. 핫스팟 재연결 후 Pi 주소는 달라질 수 있다.

1. PC와 Pi를 같은 핫스팟에 연결하고 현재 주소를 확인한다.
2. `ssh ubuntu@<현재_Pi_IP>`로 접속한다.
3. 양쪽 ROS 터미널에서 `ROS_DOMAIN_ID=4`, `ROS_LOCALHOST_ONLY=0`을 설정한다.
4. SSH와 별개로 ROS 노드·토픽 수신을 확인한다. SSH 성공만으로 DDS 통신을 검증한 것은 아니다.

실물은 Pi bringup → PC Servo·teleop 순서로 시작한다. SLAM에서는 bringup 후 Cartographer도 실행한다. 정지 시 teleop의 Space를 먼저 사용하며, 현재 키보드 코드는 키를 놓아도 마지막 속도 명령을 유지한다. 하드웨어 종료 동작과 전원 준비는 [Mission 2 실행 안내](../mission2/docs/setup-and-run.md)를 따른다.

## 입력과 시간 기준

- 시뮬레이션의 `/clock`과 실물의 시스템 시간을 혼용하지 않는다. week09 Cartographer는 `use_sim` 인자 없이, Servo는 `use_sim:=false`로 실행한다.
- camera → detector 실행에는 Image와 CameraInfo가 함께 필요하다. 기존 CSI 보정값을 C920 보정값으로 재사용하지 않는다.
- rosbag 재생 전 실시간 입력 발행을 중지하거나 별도 토픽으로 분리한다. 저장된 week08 결과는 실시간 입력을 일시 정지한 상태의 재생이다.
- `map.pgm`과 `map.yaml`은 함께 보관한다. YAML의 상대 이미지 경로가 유지되어야 한다.

## 자동 검사와 현장 검사

`python3 tools/check_repository.py`는 표준 라이브러리와 Git·Bash로 실행하며 ROS를 필요로 하지 않는다. Mission 1의 운동 제어기 시험도 ROS 없이 실행할 수 있다. CI 구성은 [GitHub의 Python 워크플로 안내](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)를 참고한다.

이 검사로 통과를 확인할 수 없는 ROS 통신·GUI·하드웨어 상태는 각 실습의 절차로 별도 확인한다. 실물 구동을 CI나 저장소 검사 스크립트가 자동으로 시작하지 않는다.
