# 2026년 2학기 지능로봇실습

Ubuntu 22.04와 ROS 2 Humble을 기반으로 로봇 소프트웨어 개발을 학습하고,
주차별 실습 코드, 실행 방법, 결과 화면 및 보고서를 정리하는 저장소입니다.

- 이름: 강태욱
- 학번: 202302200
- 실습 환경: Ubuntu 22.04, ROS 2 Humble

## 수업 소개

Linux와 ROS 2 기초부터 워크스페이스 및 패키지 구성, 노드 간 통신을 익힙니다.
이후 로봇 시각화와 시뮬레이션, 센서 데이터 처리, 지도 작성 및 자율주행,
로봇팔 모션 계획과 pick & place로 실습 범위를 넓힙니다.
학기 말에는 프로젝트를 준비하고 현장 시연과 보고서로 결과를 제출합니다.

## 주차별 강의 계획

| 주차 | 실습 | 강의 | 미션 |
| --- | --- | --- | --- |
| 1 | — | 지능로봇실습 강의 소개 | — |
| 2 | Linux & ROS 2 소개(이론), 환경 설정 준비 | 워크스페이스, 패키지 | — |
| 3 | Ubuntu 22.04·Humble 설치, Turtlesim 실행 | 노드, 토픽, 메시지 | — |
| 4 | 패키지 생성·빌드, pub/sub 노드 작성 | 서비스, 액션, 파라미터, Launch | — |
| 5 | Turtlesim 순찰 로봇, 팀 구성 확정 | 실습 장비(Waffle+OM-X) 소개 | #1 |
| 6 | 실습 장비 bringup | RViz2, RQt, Gazebo | #2 |
| 7 | RViz2, RQt, Gazebo 구동 | 좌표 변환, TF2, URDF | — |
| 8 | 중간고사(10/20) | 기말 프로젝트 공지(정의서 배포) | — |
| 9 | URDF 작성, RViz2 시각화 | 센서 데이터, rosbag2, ArUco 마커 | — |
| 10 | 센서 시각화, 마커 pose 검출 | SLAM과 지도 작성 | — |
| 11 | Cartographer로 강의실 지도 작성 | Nav2 자율주행 | — |
| 12 | 지정 지점 자율주행, 파라미터 튜닝 | MoveIt2, 순·역기구학, 모션 플래닝 | #3 |
| 13 | pick & place 구현 | YOLO·SAM·Ollama·Whisper AI 등 AI 기능 소개 | #4 |
| 14 | 프로젝트 준비 | — | — |
| 15 | 프로젝트 발표: 현장 시연 및 보고서 제출 | — | — |

## 실습 자료

각 폴더의 README에서 실행 방법과 결과를 확인할 수 있습니다.
아래 목록은 현재 저장된 자료이며, 위 강의 계획과 별도로 정리했습니다.

| 폴더 | 저장된 내용 |
| --- | --- |
| [week02](week02/) | ROS 2 설치 및 talker/listener 통신 확인, 실습 보고서 |
| [week03](week03/) | Publisher/Subscriber 패키지, 학번을 적용한 노드 실행, rqt_graph 결과 |

## 실습 장비 — Waffle + OpenMANIPULATOR-X

| 장비 | 구성 및 역할 |
| --- | --- |
| TurtleBot3 Waffle | 자율주행 베이스. 360° LiDAR로 거리 측정 및 SLAM, 카메라로 비전·ArUco 마커 인식 |
| IMU·휠 엔코더 | 자세와 주행거리 추정 |
| OpenCR 보드 | 모터·센서 저수준 제어 |
| SBC(라즈베리파이) | ROS 2 실행 |
| OpenMANIPULATOR-X | 4자유도 관절과 그리퍼, DYNAMIXEL 스마트 모터 5개로 구성된 로봇팔. MoveIt2로 모션 계획 |

Waffle 위에 로봇팔을 장착한 **모바일 매니퓰레이터**로 실습합니다.
팀별 실물 키트를 배정받고 Gazebo 시뮬레이션과 실물 연습을 병행합니다.

## 미션과 기말 프로젝트

| 미션 | 주차 | 비중 | 수행 내용 |
| --- | --- | --- | --- |
| #1 Turtlesim 순찰 | 5주차 | 5% | 사각 경로 반복 주행, 시작·정지 서비스, launch로 한 번에 실행 |
| #2 장비 Bringup | 6주차 | 5% | 팀 키트 구동, 텔레옵으로 지정 경로 주행, 로봇팔 지정 자세 |
| #3 SLAM·Nav2 | 12주차 | 5% | 강의실 지도 작성, 지정한 3지점 연속 자율주행 |
| #4 Pick & Place | 13주차 | 5% | 지점 A의 물체를 집어 지점 B에 놓기 |

### Final Project — 30%

미션 #3의 자율주행과 #4의 물체 조작에 인식을 결합해 하나의 시스템으로 구성합니다.

```text
시작 명령 → Nav2 주행 → ArUco 인식 → Pick → 배달 주행 → Place
```

- **평가:** 현장 시연, 보고서 및 시연 영상 제출. 별도 PPT 발표 없이 단계별 부분점수 부여
- **14주차:** 아레나 오픈, 지도 제작 및 연습
- **15주차:** 데모 데이
- **최대 +5 가산점:** YOLO pick, LLM 명령, 다중 배달, 동적 장애물
- **기반:** ROBOTIS 공식 `turtlebot3_home_service_challenge`의 Humble 버전 개선판. 공식 시뮬레이션 월드로 사전 연습
- **상세 규정:** 강의 소개 자료 기준 중간고사 이후 배포 예정

## 참고자료

### 공식 문서와 실습 키트

- [ROS 2 Humble](https://docs.ros.org/en/humble/)
- [Nav2](https://docs.nav2.org/)
- [MoveIt 2 Humble](https://moveit.picknik.ai/humble/index.html)
- [Cartographer ROS](https://google-cartographer-ros.readthedocs.io/)
- [ROBOTIS e-Manual — TurtleBot3 Manipulation](https://emanual.robotis.com/docs/en/platform/turtlebot3/manipulation/)
- [ROBOTIS TurtleBot3 Manipulation 소스](https://github.com/ROBOTIS-GIT/turtlebot3_manipulation)

### 강의와 교재

- [표윤석 ROS 2](https://cafe.naver.com/openrt/24070)
- [김수영 ROS 2 — Roadbalance](https://m-hakaton.tistory.com/tag/ROS2_Roadbalance)
- [표윤석 ROS 1 세미나 자료](https://github.com/robotpilot/ros-seminar)
- [표윤석 ROS 1 영상](https://www.youtube.com/playlist?list=PLRG6WP3c31_VIFtAxSke2NG_DumVZPgw)

### 추가 참고자료

- [Robotics Back-End](https://www.youtube.com/@RoboticsBackEnd)
- [ROS Wiki — URDF Tutorials](https://wiki.ros.org/urdf/Tutorials)
- [ROS Wiki — robot_state_publisher Tutorials](https://wiki.ros.org/robot_state_publisher/Tutorials)
- [Ultralytics YOLO](https://docs.ultralytics.com)
- [OpenCV ArUco 마커 검출](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)
- [Ollama](https://ollama.com)
