# 검증 근거와 해석 범위

[저장소 첫 화면](../README.md) · [재현 안내](REPRODUCIBILITY.md)

화면은 실행 상태, 로그·데이터는 관찰값, 테스트는 정해진 조건에서의 코드 동작을 보여 준다. 서로 다른 실습·입력·환경의 결과를 같은 검증으로 취급하지 않는다.

## 실습별 근거

| 실습 | 확인 방법과 원본 | 확인한 내용 | 해석 범위 |
| --- | --- | --- | --- |
| week02 | [발행](../week02/results/talker.log)·[수신](../week02/results/listener.log) 로그, [화면](../week02/screenshots/talker_202302200.png) | 기본 데모의 동일 번호 메시지 송수신 | 별도 Python 대응 코드의 실행 증거는 아님 |
| week03 | [로그](../week03/results/listener.log), [rqt_graph](../week03/screenshots/rqt_graph_202302200.png) | 학번 노드·토픽으로 메시지 전달 | 지연·처리량 벤치마크는 수행하지 않음 |
| Mission 1 | [검사 JSON](../mission1/results/patrol_demo_verification.json), [시연 영상](../mission1/results/patrol_demo_2laps.mkv), [수치 시험](../mission1/mission1_202302200/test/test_square_motion.py) | 두 바퀴, 직진·회전 중 정지·재개; 각 2초 정지 관측 | 서비스 응답 후 0.4초 안정화 뒤 측정. 정지 응답 지연이나 실물 성능은 측정하지 않음 |
| Mission 2 | [컨트롤러 화면](../mission2/screenshots/bringup-five-active.png), [주행 영상](../mission2/results/path-driving.mp4), [자세 사진](../mission2/screenshots/target-pose.jpg) | 5개 active, 수동 주행·팔 자세 변경 | 주행 영상 약 10.8초. 목표 경로 전 구간·궤적 정확도는 확인하지 않음 |
| week06 | [통합 화면](../week06/screenshots/mission_capture.png), [컨트롤러](../week06/results/controllers.txt), [관찰 기록](../week06/results/observations.md) | 시뮬레이션 센서·주행·명령 그래프 | 그래프는 실제 속도가 아닌 명령값. 캡처 전 로봇 자세 복원 |
| week07 | [URDF 검사](../week07/results/check_urdf.txt), [TF 값](../week07/results/tf2_echo_moved.txt), [TF 트리](../week07/results/frames_2026-10-26_13.41.44.pdf) | 4링크·3관절, 직선 이동 및 소각도 회전 | RViz 운동학 모델. 관성·동역학·실물 검증 아님 |
| week08 | [검사 JSON](../week08/results/verification.json), [bag DB](../week08/results/aruco_bag/aruco_bag_0.db3), [화면](../week08/screenshots/02_rosbag_play_aruco_pose.png) | CSI 카메라 ID 0, bag 영상 28개·CameraInfo 32개, 재생 pose 28개 | 강의 제공 보정값과 약 13cm 마커. 절대 거리 정확도 미검증; C920 보정 별도 |
| week09 | [PGM](../week09/results/map.pgm)·[YAML](../week09/results/map.yaml), [로그](../week09/results/cartographer_excerpt.log), [화면](../week09/screenshots/02_low_speed_mapping.png) | 실물 지도 저장, map_server 읽기·활성화, 저속화 후 벽 겹침 감소 관찰 | 일부 번짐·미관측 영역 존재. 같은 경로의 통제 비교·전체 폐루프·실측 오차 검증 아님 |

## 자동 검사

[Repository checks](../.github/workflows/verify.yml)는 push·pull request마다 다음을 실행한다. 로컬에서도 같은 명령을 사용할 수 있다.

```bash
python3 tools/check_repository.py
PYTHONPATH=mission1/mission1_202302200 \
  python3 -m unittest discover -s mission1/mission1_202302200/test -v
```

- 주차·미션 README, 코드, 사진과 결과 파일의 존재 여부
- 직접 관리하는 Markdown의 상대경로 링크·이미지 참조와 추적 파일 여부
- Python 구문, Bash 구문, XML·JSON 파싱과 PNG/JPEG/PDF 파일 표식
- 보존 작업공간 `SHA256SUMS`와 ZIP의 CRC 검사
- rosbag SQLite 무결성·토픽별 메시지 수와 메타데이터 일치
- PGM 크기·픽셀 수와 YAML·검증 기록의 연결
- 사각 순찰의 반복 경로·각도 경계·속도 제한·직진 재개 수치 시험

외부 웹 링크 가용성, 영상 내용의 진위, 카메라 보정 정확도, ROS 노드 실행과 실물 동작은 CI 범위 밖이다. Mission 2 원본 패키지 내부 README와 SDK의 과거 Python 코드는 당시 소스 보존 대상이므로 현재 문서·Python 구문 검사에서는 제외하고 원본 해시로 확인한다.

## 결과를 추가할 때

새 결과는 기존 원본을 덮어쓰지 않는 별도 경로에 저장하고 실행 환경, 입력, 설정과 관찰 범위를 함께 기록한다. 캡처에 보이는 현상과 수치 측정값을 구분한다. 비교 실험에서는 경로·속도·입력·시간 조건을 맞추거나 달라진 조건을 명시한다.
