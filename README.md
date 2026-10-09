# 2026년 2학기 지능로봇실습

Ubuntu 22.04와 ROS 2 Humble에서 노드 간 통신, turtlesim 제어와 실제 TurtleBot3 구동을 실습하고, 코드·실행 방법·관찰 결과를 정리한다.

- 이름: 강태욱
- 학번: 202302200
- 실습 환경: Ubuntu 22.04, ROS 2 Humble

## 목적

메시지 발행·구독으로 ROS 2 통신을 이해하고, Python 패키지 구성과 빌드를 거쳐 서비스와 launch를 사용하는 사각 순찰로 확장한다. 이후 원격 PC와 라즈베리파이를 연결하여 실제 로봇의 주행과 팔 조작을 수행한다.

## 진행 과정

1. **week02:** 기본 talker/listener 데모의 메시지 송수신을 확인하고, 같은 동작의 Python 코드를 작성했다.
2. **week03:** publisher와 subscriber를 `my_first_pkg`로 구성하고, 학번을 적용한 노드·토픽 연결을 rqt_graph로 확인했다.
3. **mission1:** turtlesim 사각 순찰을 구현하고, 서비스로 직진·회전 중 정지와 재개를 검증했다.
4. **mission2:** 팀 4의 TurtleBot3를 bringup하고 키보드로 바퀴 주행과 로봇팔 자세 변경을 수행했다.

## 결과 및 실습 자료

| 실습 | 확인한 결과 | 코드·실행 방법·결과 자료 |
| --- | --- | --- |
| week02 | 기본 데모의 `Hello World: N` 발행·수신 | [week02 실습 정리](week02/README.md) |
| week03 | `/chatter_202302200` 메시지 송수신 및 rqt_graph 연결 | [week03 실습 정리](week03/README.md) |
| mission1 | turtlesim 사각형 두 바퀴, 직진·회전 정지·재개와 최종 정지 | [미션 1 사각 순찰](mission1/README.md) |
| mission2 | 실제 로봇 컨트롤러 5개 활성화, 수동 주행과 팔 자세 변경 | [미션 2 코드·구조도·실행·결과](mission2/README.md) |

week02·03은 메시지 통신, mission1은 turtlesim 시뮬레이션, mission2는 실물 로봇 결과다. 각 폴더에 실행 로그·캡처·영상과 확인 범위를 정리했다.

## 실행 방법

Ubuntu에 ROS 2 Humble이 설치된 상태에서 저장소를 준비한다.

```bash
git clone https://github.com/ktw25079/Intelligent_Robot_Practice.git "$HOME/intelligent_robot_practice"
cd "$HOME/intelligent_robot_practice"
```

이미 받은 저장소는 해당 폴더에서 실습별 README를 따라 실행한다. 각 안내는 위 경로를 기준으로 하며, 다른 위치에 저장했다면 경로를 맞춘다. week02는 스크립트 또는 Python 파일을 직접 실행하고, week03는 `~/ire_ws`, mission1는 저장소의 `mission1/`를 작업공간으로 사용한다.

mission2는 원격 PC와 라즈베리파이에서 각각 빌드·실행한다. [장치별 배치·최초 빌드·네 터미널 실행](mission2/docs/setup-and-run.md)을 따른다.
