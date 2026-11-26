# Mission 4 · 정지형 Pick & Place

## 목표

베이스를 고정한 상태에서 A의 5 × 5 × 10 cm 상자를 들어 B까지 옮긴다. 한 번 실행해 여섯 단계를 연속 수행하고, B에 상자를 세운 뒤 그리퍼를 후퇴시킨다.

## 과정

실물에서 찾은 네 관절의 목표각을 `POSES`에 기록했다. 팔은 `FollowJointTrajectory`, 그리퍼는 `GripperCommand` 액션으로 제어한다. 접근 → 하강 → 파지 → 상승 → 이송 → 배치·후퇴 순으로 액션 결과를 기다린다. 이송할 때 첫 번째 관절을 약 40° 돌리고, B에서 개방·상승 후 팔을 접어 초기 자세로 돌아간다. [실행 코드](src/ire_week11_moveit/scripts/pick_demo_202302200.py)

<details>
<summary>실물에서 실행하기</summary>

피킹 위치와 관절각은 촬영 당시의 로봇·상자 배치에 맞춰져 있다. 팔 주변을 비우고 Pi에서 실물 브링업을 시작한다. 이 장비는 기본 작업공간 위에 보정 드라이버를 불러온다. [Pi 준비·브링업](../mission2/docs/setup-and-run.md)

PC를 Pi와 같은 핫스팟에 연결한다. ROS 2 Humble이 설치된 PC의 저장소 루트에서 다음 명령을 실행한다. 컨트롤러 목록에서 `arm_controller`와 `gripper_controller`가 모두 `active`이고, 팔이 브링업 자세에 있으며 상자가 A에 있을 때 마지막 줄을 실행한다.

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0
ros2 control list_controllers
python3 mission4/src/ire_week11_moveit/scripts/pick_demo_202302200.py
```

패키지로 실행하려면 같은 환경에서 저장소의 `mission4/`를 별도 작업공간으로 빌드한다.

```bash
cd mission4
colcon build --base-paths src --packages-select ire_week11_moveit
source install/setup.bash
ros2 run ire_week11_moveit pick_demo_202302200
```

</details>

## 결과

11월 26일 실물 실행 로그에서 첫 개방부터 브링업 복귀까지 160초가 걸렸다. 시연 영상에서 상자가 A를 떠나 B까지 그리퍼에 잡혀 있고, 내려놓은 뒤에도 똑바로 서 있는 모습을 확인할 수 있다. [실행 로그](results/run.log) · [시연 영상 · 2분 35초](results/mission4_202302200.mp4)

[![1분 55초, 그리퍼가 물러난 뒤 B에 세워진 상자](screenshots/placement.jpg)](results/mission4_202302200.mp4)
