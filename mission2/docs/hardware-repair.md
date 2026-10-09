# 하드웨어 통신 보정과 점검

[미션 2로 돌아가기](../README.md)

## 1. 기본 소스와 보정 소스를 함께 보존한 이유

Pi의 `turtlebot3_ws`는 기본 하드웨어 패키지, `lecture05-repair_ws`는 수정 드라이버와 SDK를 포함한다. 시작 스크립트는 기본 작업공간 뒤에 보정 작업공간을 source한다. 기본 소스가 남아 있다고 실제 실행에서도 기본 드라이버만 사용한 것으로 해석하지 않는다.

수정 내용은 코드·patch로 확인할 수 있지만, 실패 당시 전체 로그나 수정 전후 통신 성공률 측정은 없다. 아래는 적용된 코드의 역할을 설명하며 특정 오류가 이 수정 하나로 완전히 해결되었다고 단정하지 않는다.

## 2. 사전 점검 스크립트

[preflight-robot.py](../workspaces/raspberry-pi/home/ubuntu/lecture05-setup/preflight-robot.py)는 다음 순서로 검사한다.

| 검사 | 목적 | 한계 |
| --- | --- | --- |
| 환경 변수·ROS 패키지 | 팀 도메인·LiDAR 및 필요한 패키지 준비 | 실제 프로세스 활성화 검사는 아님 |
| 시리얼 접근·점유 | `/dev/ttyACM0`, `/dev/ttyUSB0` 사용 가능 여부 | 모터 움직임은 시험하지 않음 |
| Pi 전원 플래그 | 현재·관찰 중 저전압/스로틀링 표시 확인 | 배터리의 전체 상태 진단은 아님 |
| OpenCR PING/READ | ID 200, 1,000,000 baud에서 응답과 제어 테이블 확인 | 펌웨어 전체 기능 시험은 아님 |
| 모델·연결 플래그 | Waffle_OpenManipulator와 팔·바퀴 연결 상태 확인 | 부팅 시 연결 플래그와 물리 동작은 구분 |

JSON에는 입력 전압도 기록하도록 되어 있다. 이는 OpenCR 입력 전압이며 Pi의 5 V 공급 전압과 같다고 쓰지 않는다. `physical_clearance_checked=False`이므로 주변 공간은 사람이 별도로 확인한다. 실제 생성된 JSON은 보존본에 없다.

## 3. OpenCR 응답 대기 시간

수정 [dynamixel_sdk_wrapper.cpp](../workspaces/raspberry-pi/home/ubuntu/lecture05-repair_ws/src/turtlebot3_manipulation_hardware/src/dynamixel_sdk_wrapper.cpp)는 Linux 포트 클래스를 확장하여 대기 시간을 제어한다.

```cpp
double response_timeout_ms = 100.0;
void setPacketTimeout(uint16_t) override {
  PortHandlerLinux::setPacketTimeout(response_timeout_ms);
}
```

쓰기 요청에서는 다음과 같이 구분한다.

```cpp
ScopedResponseTimeout timeout(*static_cast<OpenCRPortHandler *>(port_handler_),
  address == 59 && length == 1 ? 6500.0 : 100.0);
```

일반 요청은 100 ms, IMU 재보정 주소 59에 대한 1바이트 요청은 6,500 ms로 처리한다. 소스 주석은 IMU 보정이 펌웨어 안에서 동기 처리되어 최대 약 5초 걸릴 수 있다고 설명한다. Scoped 객체는 해당 요청 후 기존 대기 시간을 복원한다. 이 값들은 코드상 설정이며 실제 응답 지연 측정 결과가 아니다.

## 4. IMU 보정 요청 실패를 확인한다

수정 [opencr.cpp](../workspaces/raspberry-pi/home/ubuntu/lecture05-repair_ws/src/turtlebot3_manipulation_hardware/src/opencr.cpp):

```cpp
void OpenCR::imu_recalibration()
{
  uint8_t request = 1;
  if (!dxl_sdk_wrapper_->write(opencr_control_table.imu_re_calibration.address, 1, &request)) {
    throw std::runtime_error("OpenCR IMU recalibration acknowledgement failed");
  }
}
```

보정 요청 1을 명시적으로 쓰고 응답 실패 시 예외를 발생시킨다. 1바이트 읽기 함수도 버퍼를 0으로 초기화하고 통신 실패를 확인하도록 수정되어 있다. 관련 [변경 패치](../workspaces/jetson/home/jetson/ire_ws/lecture05-live/diagnostics/hardware-opencr-response.patch)에서 기본 코드와 비교할 수 있다.

## 5. DynamixelSDK 수신 처리 보정

[SDK patch](../workspaces/jetson/home/jetson/ire_ws/lecture05-live/diagnostics/sdk-repro/sdk-4.0.3-receive-safety.patch)의 핵심은 다음 세 가지다.

1. 패킷 길이의 하한과 버퍼 한계를 검사한다.
2. 수신 버퍼를 `RXPACKET_MAX_LEN` 크기로 확보하도록 변경한다.
3. 요청의 ID와 예상 응답 길이를 확인하고 일치하지 않는 늦은 응답을 timeout 안에서 걸러낸다.

예를 들어 READ 응답이 늦게 도착해 뒤의 WRITE 응답으로 처리되는 상황을 고려한 코드다. 여기서 실제 패킷 혼선 빈도나 성능 개선량을 측정한 결과는 제공되지 않았다.

보정 SDK 원본은 [sdk-4.0.3-fixed](../workspaces/raspberry-pi/home/ubuntu/lecture05-setup/sdk-4.0.3-fixed/)에 있다. `diagnostics/`는 당시 조사·재현용 소스이며 일반 실행 순서에는 포함하지 않는다. 포트 스캔·쓰기 probe를 bringup과 동시에 실행하는 절차로 안내하지 않는다.

## 6. 실제 캡처의 경고와 오류

| 화면 메시지 | 확인 가능한 의미 | 결과에 미치는 해석 |
| --- | --- | --- |
| `servo node joint2/joint3 close to a position limit. Halting.` | Servo가 관절 한계 접근을 감지해 정지 메시지를 출력 | 팔 입력이 있어도 제한 조건에 따라 동작이 멈출 수 있음 |
| `No 3D sensor plugin(s) defined for octomap updates` | Octomap 갱신용 센서 플러그인 미설정 | 3D 장애물 지도 갱신 성공을 주장할 수 없음 |
| `Link end_effector_link has visual geometry but no collision geometry` | 해당 링크의 시각 모델과 충돌 모델 구성 차이 | 외형이 보여도 모든 링크의 충돌 모델이 완비된 것은 아님 |
| `Resolution not specified for Octomap. Assuming resolution = 0.1 instead` | 해상도 미지정으로 기본값 사용 | 지도 정확도·장애물 인식 성능을 입증하는 수치가 아님 |

세 번째 메시지는 [Servo 연결 직후 화면](../screenshots/mission2-ready-final.png)에 있다. 관절 한계 경고는 [사용자 4분할 화면](../screenshots/four-terminals.png)에 있다. 두 캡처는 서로 다른 시점의 자료이며 경고를 지워 하나의 완전 정상 화면처럼 재구성하지 않았다.

## 7. 문제가 있을 때 확인할 계층

1. IP 통신: 같은 Wi-Fi인지, Pi 주소가 `.21`인지, PC `.204`와 혼동하지 않았는지 확인.
2. ROS 통신: 각 터미널의 domain·localhost 설정과 source 여부 확인.
3. 구동: 포트·패키지·OpenCR 점검 후 다섯 컨트롤러 상태 확인.
4. 바퀴: teleop 포커스, `/cmd_vel` 값과 Space 정지 동작 확인.
5. 팔: Servo 프로세스·서비스와 관절 한계 메시지 확인.
6. 실제 결과: 사진·영상·수치 로그가 어느 확인 항목을 뒷받침하는지 분리.

이 순서는 문제를 좁혀 가는 설명이며, 나열한 모든 문제가 이번 실습에서 발생했다는 뜻은 아니다.
