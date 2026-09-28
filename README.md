# 2026년 2학기 지능로봇실습

Ubuntu 22.04와 ROS 2 Humble에서 노드 간 통신과 turtlesim 제어를 실습하고, 코드·실행 방법·관찰 결과를 정리한다.

- 이름: 강태욱
- 학번: 202302200
- 실습 환경: Ubuntu 22.04, ROS 2 Humble

## 목적

메시지 발행·구독으로 ROS 2 통신을 이해하고, Python 패키지 구성과 빌드를 거쳐 서비스와 launch를 사용하는 사각 순찰로 확장한다.

## 진행 과정

1. **week02:** 기본 talker/listener 데모의 메시지 송수신을 확인하고, 같은 동작의 Python 코드를 작성했다.
2. **week03:** publisher와 subscriber를 `my_first_pkg`로 구성하고, 학번을 적용한 노드·토픽 연결을 rqt_graph로 확인했다.
3. **week04:** turtlesim 사각 순찰을 구현하고, 서비스로 직진·회전 중 정지와 재개를 검증했다.

## 결과 및 실습 자료

| 주차 | 확인한 결과 | 코드·실행 방법·결과 자료 |
| --- | --- | --- |
| week02 | 기본 데모의 `Hello World: N` 발행·수신 | [week02 실습 정리](week02/README.md) |
| week03 | `/chatter_202302200` 메시지 송수신 및 rqt_graph 연결 | [week03 실습 정리](week03/README.md) |
| week04 | turtlesim 사각형 두 바퀴, 직진·회전 정지·재개와 최종 정지 | [week04 실습 정리](week04/README.md) |

week02·03에는 실행 로그와 캡처, week04에는 시뮬레이터 시연 영상과 정지 전후 측정값을 저장했다. week04의 측정값은 turtlesim 결과다.

## 실행 방법

Ubuntu에 ROS 2 Humble이 설치된 상태에서 저장소를 준비한다.

```bash
git clone https://github.com/ktw25079/Intelligent_Robot_Practice.git "$HOME/intelligent_robot_practice"
cd "$HOME/intelligent_robot_practice"
```

이미 받은 저장소는 해당 폴더에서 주차별 README를 따라 실행한다. 각 안내는 위 경로를 기준으로 하며, 다른 위치에 저장했다면 경로를 맞춘다. week02는 스크립트 또는 Python 파일을 직접 실행하고, week03는 `~/ire_ws`, week04는 저장소의 `week04/`를 작업공간으로 사용한다.
