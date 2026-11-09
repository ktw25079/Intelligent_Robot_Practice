# 코드 출처와 기여 범위

[저장소 첫 화면](../README.md)

| 범위 | 기반 자료 | 이 저장소의 구현·적용 | 원본·근거 |
| --- | --- | --- | --- |
| week02 | ROS 2 talker/listener 데모 | 실행 스크립트와 대응 Python 코드, 송수신 결과 정리 | [코드](../week02/talker.py) · [로그](../week02/results/talker.log) |
| week03 | ROS 2 Python pub/sub 패턴 | 패키지·실행 진입점, 이름 파라미터, 학번 remapping | [패키지](../week03/my_first_pkg/) · [실행 스크립트](../week03/run_pubsub.sh) |
| Mission 1 | ROS 2 turtlesim·SetBool 인터페이스 | pose 기반 사각 순찰 제어기, ROS 어댑터, 상태 보존, 시연 검사·수치 시험 | [제어기](../mission1/mission1_202302200/mission1_202302200/square_motion.py) · [라이선스](../mission1/mission1_202302200/LICENSE) |
| Mission 2 | ROBOTIS TurtleBot3 Manipulation·DynamixelSDK, 팀원 제공 작업공간 | 본인 노트북 연결·팀 환경 구성 및 실물 운용; 팀 소스·통신 보정과 결과 정리 | [보존본 출처](../mission2/workspaces/README.md) · [작성자 기록](../mission2/workspaces/CONTENTS.json) |
| week06 | ROBOTIS 시뮬레이션 소스 | Gazebo·RViz·Plot 통합 launch, 베이스 teleop, 표시 설정 | [launch](../week06/mission.launch.py) · [고정 커밋과 재현 명령](../week06/README.md) |
| week07 | 강의 launch 구성 | 4링크 URDF 직접 설계, 모델 경로·RViz 설정, 운동학과 TF 비교 | [URDF](../week07/myurdf_202302200.urdf) · [launch](../week07/launch/display.launch.py) |
| week08 | iCIR 강의 ArUco·색 검출 예제, 강의 카메라 보정값 | 실물 토픽·마커 크기 적용, 패키지 진입점, 수신·재생 검사, C920 연결 도구 | [검출기](../week08/ire_week08_vision/ire_week08_vision/aruco_detect.py) · [검사기](../week08/scripts/check_topics.py) |
| week09 | Mission 2의 ROBOTIS 패키지·Cartographer | 실물 SLAM 운용, teleop 속도 상한 변경, 실행·저장 도구와 결과 검증 | [teleop](../week09/turtlebot3_manipulation_teleop/) · [라이선스](../week09/turtlebot3_manipulation_teleop/LICENSE) |

강의 예제나 팀 제공 드라이버를 새로운 알고리즘의 독자 구현으로 표현하지 않는다. 개발·수정한 부분과 설치·운용·검증한 부분을 각 실습 문서에서 구분한다.

## 보존 원칙

Mission 2의 소스는 당시 제공된 구조와 저작권·라이선스 표시를 유지한다. 원본 일반 파일 해시는 [SHA256SUMS](../mission2/workspaces/SHA256SUMS)로 확인한다. SDK의 절대 심볼릭 링크는 당시 Pi 배치용이며 GitHub 화면에서 직접 열리지 않을 수 있다. [설치 경로 안내](../mission2/docs/setup-and-run.md)를 따른다.

각 파일·패키지의 기존 라이선스와 저작권 표시가 해당 소스에 적용된다. 이 저장소 전체에 단일 라이선스가 적용된다고 가정하지 않는다.
