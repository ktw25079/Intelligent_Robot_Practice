# 핵심 코드 해설

[미션 2로 돌아가기](../README.md)

코드는 제공된 2026-10-08 보존본 기준이다. 아래 발췌는 전체 실행 파일이 아니라 해당 동작을 설명하는 부분이다. ROBOTIS 원본 패키지, 팀 실행 스크립트, 수정 드라이버를 구분한다.

## 1. 파일을 읽는 순서

| 단계 | 파일 | 핵심 역할 |
| --- | --- | --- |
| 환경 | [robot-env.bash](../workspaces/jetson/home/jetson/ire_ws/lecture05-live/robot-env.bash) | PC 환경 source, 팀 도메인과 LiDAR 지정 |
| Pi 시작 | [bringup-robot.sh](../workspaces/raspberry-pi/home/ubuntu/lecture05-setup/bringup-robot.sh) | 사전 점검과 보정 overlay 적용 후 launch |
| 하드웨어 launch | [hardware.launch.py](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_bringup/launch/hardware.launch.py) | base launch와 LiDAR launch 포함 |
| 컨트롤러 구성 | [base.launch.py](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_bringup/launch/base.launch.py) | 모델, controller_manager, broadcaster·controller 활성화 |
| 팔 Servo | [servo.launch.py](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_moveit_config/launch/servo.launch.py) | 로봇 모델·운동학·Servo 설정을 노드에 전달 |
| 키보드 | [teleop.cpp](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_teleop/src/turtlebot3_manipulation_teleop.cpp) | 키 입력을 주행·관절·그리퍼 명령으로 변환 |
| 상수 | [teleop.hpp](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_teleop/include/turtlebot3_manipulation_teleop/turtlebot3_manipulation_teleop.hpp) | 토픽 이름, 속도 증분, 키 코드 |

## 2. 환경을 불러오는 순서

```bash
source /opt/ros/humble/setup.bash
source "$HOME/turtlebot3_ws/install/setup.bash"
source "$HOME/lecture05-repair_ws/install/setup.bash"
export ROS_DOMAIN_ID=4 ROS_LOCALHOST_ONLY=0 LDS_MODEL=LDS-01
```

첫 줄은 ROS 2 Humble, 두 번째는 로봇 기본 패키지, 세 번째는 수정 SDK·드라이버 환경이다. 같은 이름의 패키지가 기본 작업공간과 보정 작업공간에 모두 있으므로 마지막 overlay가 무엇인지 확인해야 한다. 실행 위치는 Pi다.

PC의 `robot-env.bash`는 `~/ire_ws/env.bash`를 통해 Humble과 PC 작업공간을 불러온다. 이 파일에 Gazebo 환경 처리도 있지만 이번 `use_sim:=false` 실행이 Gazebo 실험이라는 의미는 아니다.

## 3. Bringup은 여러 기능을 묶어서 실행한다

`hardware.launch.py`는 `LDS_MODEL`을 읽어 LDS-01이면 `hls_lfcd_lds_driver`의 `hlds_laser.launch.py`를 선택한다. LiDAR 포트는 `/dev/ttyUSB0`, 프레임은 `base_scan`으로 전달한다. 동시에 `base.launch.py`를 포함한다.

`base.launch.py`는 xacro를 통해 로봇 모델을 전개하고 `robot_state_publisher`와 `controller_manager/ros2_control_node`를 실행한다. 이어 다섯 컨트롤러·브로드캐스터를 spawner로 준비한다. 상태 broadcaster 종료 이벤트 이후 나머지 spawner를 시작하는 구성이 있으므로 로그가 순차적으로 보인다.

컨트롤러 구성 발췌:

```yaml
controller_manager:
  ros__parameters:
    update_rate: 100
    diff_drive_controller:
      type: diff_drive_controller/DiffDriveController
    arm_controller:
      type: joint_trajectory_controller/JointTrajectoryController
    gripper_controller:
      type: position_controllers/GripperActionController
```

중간의 `joint_state_broadcaster`·`imu_broadcaster` 항목은 위 발췌에서 생략했다. 전체 설정은 [hardware_controller_manager.yaml](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_bringup/config/hardware_controller_manager.yaml)에 있다.

## 4. 키 입력을 읽는 방식

`KeyboardReader`는 터미널의 `ICANON`과 `ECHO`를 해제하여 Enter를 기다리지 않고 한 글자를 읽도록 구성한다. `KeyboardServo::keyLoop()`는 읽은 키를 switch문으로 분기한다. 이 때문에 키보드 입력을 받을 터미널이 실제로 선택되어 있어야 한다.

생성하는 노드와 통신 객체:

```cpp
nh_ = rclcpp::Node::make_shared("servo_keyboard_input");

base_twist_pub_ =
  nh_->create_publisher<geometry_msgs::msg::Twist>(BASE_TWIST_TOPIC, ROS_QUEUE_SIZE);
joint_pub_ = nh_->create_publisher<control_msgs::msg::JointJog>(ARM_JOINT_TOPIC, ROS_QUEUE_SIZE);
client_ = rclcpp_action::create_client<control_msgs::action::GripperCommand>(
  nh_, "gripper_controller/gripper_cmd");
```

상수 `BASE_TWIST_TOPIC`은 `cmd_vel`, `ARM_JOINT_TOPIC`은 `/servo_node/delta_joint_cmds`다. namespace가 없는 이번 구성에서는 속도 토픽이 `/cmd_vel`로 나타난다.

## 5. 바퀴 속도는 누적해서 조절한다

`i` 키 분기 발췌:

```cpp
case KEYCODE_I:
  cmd_vel_.linear.x =
    std::min(cmd_vel_.linear.x + BASE_LINEAR_VEL_STEP, BASE_LINEAR_VEL_MAX);
  cmd_vel_.linear.y = 0.0;
  cmd_vel_.linear.z = 0.0;
  RCLCPP_INFO_STREAM(nh_->get_logger(), "LINEAR VEL : " << cmd_vel_.linear.x);
  break;
```

`j` 키 분기 발췌:

```cpp
case KEYCODE_J:
  cmd_vel_.angular.x = 0.0;
  cmd_vel_.angular.y = 0.0;
  cmd_vel_.angular.z =
    std::min(cmd_vel_.angular.z + BASE_ANGULAR_VEL_STEP, BASE_ANGULAR_VEL_MAX);
  RCLCPP_INFO_STREAM(nh_->get_logger(), "ANGULAR VEL : " << cmd_vel_.angular.z);
  break;
```

| 키 | 상태 변화 |
| --- | --- |
| `i` | 선속도 +0.01 m/s, 최대 +0.26 m/s |
| `k` | 선속도 −0.01 m/s, 최소 −0.26 m/s |
| `j` | 각속도 +0.1 rad/s, 최대 +1.8 rad/s |
| `l` | 각속도 −0.1 rad/s, 최소 −1.8 rad/s |
| `Space` | Twist 전체 초기화, 바퀴 정지 명령 |

0에서 `i`를 한 번 누르면 명령값은 0.01 m/s, 두 번 누르면 0.02 m/s가 된다. 이는 **코드 동작을 설명하는 예**이며 당시 측정 로그가 아니다. `k`는 무조건 즉시 후진시키는 키가 아니라 현재 선속도를 줄이는 키다. 양수 상태에서는 감속한 후 0을 지나 음수가 될 때 후진 명령이 된다.

또한 선속도 키는 각속도를 지우지 않고, 회전 키는 선속도를 지우지 않는다. 둘 다 0이 아니면 곡선 주행 명령이 된다. 제자리 회전을 구분해서 하려면 먼저 Space로 속도를 초기화한다.

정지 분기:

```cpp
case KEYCODE_SPACE:
  cmd_vel_ = geometry_msgs::msg::Twist();
  RCLCPP_INFO_STREAM(nh_->get_logger(), "STOP base");
  break;
```

## 6. 키를 놓아도 마지막 주행 명령을 발행한다

발행 루프의 바퀴 부분:

```cpp
base_twist_pub_->publish(cmd_vel_);
rclcpp::sleep_for(std::chrono::milliseconds(10));
```

별도 스레드에서 이 부분을 반복하므로 키 입력이 없더라도 마지막 `cmd_vel_`을 계속 보낸다. 10 ms sleep을 기준으로 약 100 Hz를 의도한 구성이나, 실행 시간과 스케줄링이 더해지므로 실측 100 Hz를 보장하는 표현은 쓰지 않는다.

컨트롤러에는 `cmd_vel_timeout: 0.5`가 있지만, teleop이 마지막 값을 계속 발행하면 이 timeout은 키를 놓는 동작으로 발생하지 않는다. 그래서 Space 정지 입력을 별도로 사용한다. Space는 여기서 바퀴 명령 초기화이며 로봇 전체의 전원 차단 기능이 아니다.

## 7. 팔 관절은 JointJog로 보낸다

```cpp
case KEYCODE_1:
  joint_msg_.joint_names.push_back("joint1");
  joint_msg_.velocities.push_back(ARM_JOINT_VEL);
  publish_joint_ = true;
  RCLCPP_INFO_STREAM(nh_->get_logger(), "Joint1 +");
  break;
```

`q` 키는 같은 관절 이름과 `-ARM_JOINT_VEL`을 사용한다. `2/w`, `3/e`, `4/r`도 각각 joint2·3·4를 같은 방식으로 선택한다. 매 키 처리 전에 이름과 속도 벡터를 비우므로 한 번의 처리에서 선택된 관절 명령을 구성한다.

```cpp
if (publish_joint_) {
  joint_msg_.header.stamp = nh_->now();
  joint_msg_.header.frame_id = BASE_FRAME_ID;
  joint_pub_->publish(joint_msg_);
  publish_joint_ = false;
  RCLCPP_INFO_STREAM(nh_->get_logger(), "Joint PUB");
}
```

바퀴와 달리 관절 명령은 발행 플래그가 있을 때 전송한 후 플래그를 내린다. `BASE_FRAME_ID`는 `link0`이다. 지정 자세를 만드는 목표 각도 배열이나 자동 자세 전환 루틴은 이 키보드 코드에 없다.

헤더에는 `ARM_JOINT_VEL = 10.0`과 rad/s 주석이 있지만, [moveit_servo.yaml](../workspaces/jetson/home/jetson/ire_ws/src/turtlebot3_manipulation/turtlebot3_manipulation_moveit_config/config/moveit_servo.yaml)은 `command_in_type: unitless`, `scale.joint: 0.5`로 설정되어 있다. 이 상수 하나를 실제 관절 속도 10 rad/s로 보고하면 안 된다. 입력 크기와 Servo 설정 사이에 검토할 부분이 있으며, 본 자료에서는 코드를 변경하거나 실제 관절 속도를 측정하지 않았다.

Servo 설정에는 `incoming_command_timeout: 0.1`, `joint_limit_margin: 0.1`도 있다. 팔 입력의 시간 제한과 관절 한계 처리는 바퀴의 0.5초 timeout과 별개의 설정이다.

## 8. 그리퍼는 액션 목표를 보낸다

```cpp
case KEYCODE_O:
  send_goal(0.025);
  RCLCPP_INFO_STREAM(nh_->get_logger(), "Gripper Open");
  break;
case KEYCODE_P:
  send_goal(-0.015);
  RCLCPP_INFO_STREAM(nh_->get_logger(), "Gripper Close");
  break;
```

`send_goal()`은 `GripperCommand::Goal`의 `command.position`을 설정하고 `async_send_goal()`로 전달한다. 제공 자료에서는 개폐 기능을 별도로 계측·검증한 로그가 없으므로 구현 내용과 검증 결과를 구분한다.

## 9. Servo 시작 서비스

teleop은 `/servo_node/start_servo`와 `/servo_node/stop_servo`의 Trigger 클라이언트를 만든다. 시작 시 서비스를 기다린 뒤 시작 요청을 보낸다. 캡처의 `SUCCESS TO CONNECT SERVO START SERVER`와 `SUCCESS to start 'moveit_servo'`가 이 코드 경로에 대응한다.

다만 코드의 성공 출력은 future가 준비되었다는 조건에서 발생하며 `Trigger` 응답의 `success` 값을 따로 검사하지 않는다. 따라서 이 문구만으로 모든 팔 동작을 검증했다고 쓰지 않고, 실제 자세 사진과 함께 판단한다.

## 10. 설정값과 측정값을 구분한다

| 값 | 출처 | 해석 |
| --- | --- | --- |
| 100 Hz | controller_manager 설정 | 설정 주기, 지터 측정 아님 |
| 0.26 m/s | teleop 최대 선속도 | 명령 제한, 영상 속도 측정 아님 |
| 1.8 rad/s | teleop 최대 각속도 | 입력 노드 제한 |
| 1.82 rad/s | diff_drive 설정 | 컨트롤러 제한, teleop 상수와 다름 |
| 0.287 m / 0.033 m | 바퀴 간격 / 반지름 설정 | 모델 파라미터, 이번 실습 실측 아님 |
| `open_loop: true` | 주행 컨트롤러 | 명령 기반 오도메트리 |
| 초기·지정 자세 | 실물 사진 | 형상 변화 확인, 각도 오차 수치 없음 |
