# Intelligent Robot Practice

**ROS 2 통신에서 실물 로봇 제어·시각 인식·SLAM·Nav2까지, 코드와 실행 근거를 함께 기록한 실습 저장소.**

강태욱 · 202302200 · 2026년 2학기 · Ubuntu 22.04 / ROS 2 Humble

[![Repository checks](https://github.com/ktw25079/Intelligent_Robot_Practice/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/ktw25079/Intelligent_Robot_Practice/actions/workflows/verify.yml)

[실습별 코드](#실습-목록) · [재현 안내](docs/REPRODUCIBILITY.md) · [검증 범위](docs/EVIDENCE.md) · [코드 출처와 기여](docs/PROVENANCE.md)

## 대표 결과

<table>
<tr>
<td width="50%" align="center" valign="top">
<a href="mission1/README.md"><img src="mission1/screenshots/overview.svg" width="420" height="236" alt="Mission 1 · 사각 순찰"/></a><br/>
<strong><a href="mission1/README.md">Mission 1 · 사각 순찰</a></strong><br/>
정지·재개와 두 바퀴 주행
</td>
<td width="50%" align="center" valign="top">
<a href="mission2/README.md"><img src="mission2/screenshots/overview.svg" width="420" height="236" alt="Mission 2 · 실물 제어"/></a><br/>
<strong><a href="mission2/README.md">Mission 2 · 실물 제어</a></strong><br/>
컨트롤러 5개 활성화·팔 자세 변경
</td>
</tr>
<tr>
<td width="50%" align="center" valign="top">
<a href="mission3/README.md"><img src="mission3/screenshots/overview.svg" width="420" height="236" alt="Mission 3 · 자율주행"/></a><br/>
<strong><a href="mission3/README.md">Mission 3 · 자율주행</a></strong><br/>
A→B 순차 이동·장애물 회피 장면
</td>
<td width="50%" align="center" valign="top">
<a href="week07/README.md"><img src="week07/screenshots/overview.svg" width="420" height="236" alt="week07 · 로봇 모델"/></a><br/>
<strong><a href="week07/README.md">week07 · 로봇 모델</a></strong><br/>
4링크·3종 관절과 TF 확인
</td>
</tr>
<tr>
<td width="50%" align="center" valign="top">
<a href="week08/README.md"><img src="week08/screenshots/overview.svg" width="420" height="236" alt="week08 · 시각 인식"/></a><br/>
<strong><a href="week08/README.md">week08 · 시각 인식</a></strong><br/>
ArUco ID·pose 검출과 기록·재생
</td>
<td width="50%" align="center" valign="top">
<a href="week09/README.md"><img src="week09/screenshots/overview.svg" width="420" height="236" alt="week09 · 지도 작성"/></a><br/>
<strong><a href="week09/README.md">week09 · 지도 작성</a></strong><br/>
저속 매핑·지도 저장·재로드
</td>
</tr>
</table>

SLAM 지도에는 일부 미관측 영역과 번짐이 남아 있다. 각 실습에서 실행 근거와 확인 범위를 볼 수 있다.

## 구현에서 검증까지

- **제어 구조:** 사각 순찰의 운동 제어기를 ROS 노드와 분리했다. 첫 방향을 기준으로 회전 목표를 정하고 정지 시 현재 변과 단계를 유지한다. [제어기](mission1/mission1_202302200/mission1_202302200/square_motion.py) · [수치 시험](mission1/mission1_202302200/test/test_square_motion.py)
- **관측 가능한 결과:** 화면뿐 아니라 서비스 응답, pose, TF, rosbag과 지도 파일을 보관한다. 실시간 입력과 bag 재생을 분리해 검출 재현 여부를 확인했다. [재생 검사값](week08/results/verification.json)
- **오류 분석:** 카메라 촬영 시간 초과의 케이블·모듈 비교, OpenCR 통신 보정, 회전 속도와 이중벽을 실행 근거와 함께 설명한다. [카메라](week08/docs/troubleshooting.md) · [OpenCR](mission2/docs/hardware-repair.md) · [SLAM](week09/README.md)

```mermaid
flowchart LR
    A[week02·03<br/>토픽 통신] --> B[Mission 1<br/>상태·서비스 제어]
    B --> C[Mission 2 · week06<br/>실물 bringup · 시뮬레이션]
    C --> D[week07<br/>모델·좌표계]
    D --> E[week08<br/>카메라·pose·재생]
    E --> F[week09<br/>실물 지도·저장]
    F --> G[Mission 3<br/>Nav2 목표 주행]
```

## 실습 목록

| 실습 | 구현·적용한 내용 | 확인한 결과 | 실행 환경 |
| --- | --- | --- | --- |
| [week02](week02/README.md) | 기본 pub/sub 데모와 Python 대응 코드 | 같은 번호의 메시지 발행·수신 로그 | PC / ROS 데모 |
| [week03](week03/README.md) | Python 패키지·파라미터·remapping | 학번 노드·토픽, rqt_graph 연결 | PC / ROS 노드 |
| [Mission 1](mission1/README.md) | pose 기반 사각 순찰, SetBool 정지·재개 | 두 바퀴 시연, 직진·회전 정지 검사 | turtlesim |
| [Mission 2](mission2/README.md) | 팀 제공 ROBOTIS 작업공간 구성·실물 운용 | 컨트롤러 5개 active, 수동 주행·팔 자세 | Pi + TurtleBot3 |
| [week06](week06/README.md) | Gazebo·RViz·RQt 통합, 베이스 teleop | LaserScan·영상·속도 명령 그래프 | Gazebo |
| [week07](week07/README.md) | URDF 4링크·3종 관절, launch 설정 | 관절 슬라이더와 TF 변환·트리 | RViz / TF |
| [week08](week08/README.md) | 강의 ArUco 예제의 실물 적용·rosbag 검증 | CSI 카메라 ID·pose 재생, C920 ID 검출 | Pi 카메라 + PC |
| [week09](week09/README.md) | Cartographer 운용·저속 제한·저장 도구 | 157×165셀 지도, 0.05m/셀, 파일 재로드 | 실물 SLAM |
| [Mission 3](mission3/README.md) | Nav2 목표 전송·A→B 순차 주행·장애물 회피 | 실물 영상 2개, RViz 녹화, A·B 성공 로그 | 실물 Nav2 |

week02의 저장 로그는 기본 데모 결과다. Mission 2는 팀 실습 자료이며, week08의 C920 보정·pose 재생과 week09의 전체 공간 폐루프 검증은 완료 확인 전이다. [근거와 한계 전체 보기](docs/EVIDENCE.md)

## 시작하기

```bash
git clone https://github.com/ktw25079/Intelligent_Robot_Practice.git ~/intelligent_robot_practice
cd ~/intelligent_robot_practice

# ROS·하드웨어 없이 저장소 자료와 제어기 수치 시험 확인
python3 tools/check_repository.py
PYTHONPATH=mission1/mission1_202302200 \
  python3 -m unittest discover -s mission1/mission1_202302200/test -v
```

동일 이름의 패키지가 있으므로 `colcon build`는 **각 실습 README에 지정된 작업공간**에서 실행한다. [장치·작업공간·통신 설정](docs/REPRODUCIBILITY.md)

CI는 문서·소스·데이터 검사와 사각 순찰 수치 시험을 실행한다. [자동 검사 항목](docs/EVIDENCE.md#자동-검사)

## 자료 구조와 출처

각 실습의 `README.md`는 **목표 → 과정 → 결과**, `screenshots/`는 화면·사진, `results/`는 로그·측정값·영상·지도다. Mission 2의 `workspaces/`는 팀 제공 소스다.

직접 작성한 제어기·URDF, 강의 예제 적용, ROBOTIS와 팀 제공 소스를 구분하고 원본 라이선스를 보존한다. [파일별 출처와 수정 범위](docs/PROVENANCE.md)
