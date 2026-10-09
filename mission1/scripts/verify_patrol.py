"""실제 ROS 서비스와 pose로 시연 순서 및 정지 상태를 검증한다."""
import json
import math
from pathlib import Path
import time

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log
from std_srvs.srv import SetBool
from turtlesim.msg import Pose


def main():
    rclpy.init()
    node = Node('patrol_verification')
    pose = None
    laps = 0

    def receive_pose(message):
        nonlocal pose
        pose = message

    def receive_log(message):
        nonlocal laps
        if message.name == 'patrol' and message.msg.startswith('Lap '):
            laps = int(message.msg.split()[1])

    node.create_subscription(Pose, '/turtle1/pose', receive_pose, 10)
    node.create_subscription(Log, '/rosout', receive_log, 100)
    client = node.create_client(SetBool, '/start_stop')
    results = {}

    def wait_for(predicate, timeout=90):
        deadline = time.monotonic() + timeout
        while not predicate():
            if time.monotonic() > deadline:
                raise TimeoutError('시연 조건 대기 시간 초과')
            rclpy.spin_once(node, timeout_sec=0.02)

    def delay(seconds):
        deadline = time.monotonic() + seconds
        wait_for(lambda: time.monotonic() >= deadline, seconds + 2)

    def request(enabled):
        print(f'/start_stop std_srvs/srv/SetBool data: {str(enabled).lower()}', flush=True)
        future = client.call_async(SetBool.Request(data=enabled))
        wait_for(future.done, 5)
        response = future.result()
        assert response.success, response.message
        print(f'success: {response.success} | {response.message}', flush=True)

    def snapshot():
        return {key: getattr(pose, key) for key in
                ('x', 'y', 'theta', 'linear_velocity', 'angular_velocity')}

    def pause(label):
        request(False)
        delay(0.4)
        before = snapshot()
        delay(2)
        after = snapshot()
        distance = math.hypot(after['x'] - before['x'], after['y'] - before['y'])
        angle = abs(math.atan2(math.sin(after['theta'] - before['theta']),
                              math.cos(after['theta'] - before['theta'])))
        results[label] = dict(before=before, after=after,
                              position_drift=distance, angle_drift=angle,
                              observation_seconds=2.0)
        assert distance < 0.001 and angle < 0.001
        assert after['linear_velocity'] == 0 and after['angular_velocity'] == 0
        print(f'정지 검증: 위치 변화 {distance:.6f}, 각도 변화 {angle:.6f} rad\n', flush=True)

    try:
        print('mission1_202302200 | 서비스 시연 및 실측 검증\n', flush=True)
        assert client.wait_for_service(timeout_sec=15)
        wait_for(lambda: pose is not None, 10)
        delay(3)
        print('[1/6] 사각 순찰 시작', flush=True)
        request(True)
        wait_for(lambda: pose.linear_velocity > 0.1)
        delay(0.4)
        print('[2/6] 직진 중 정지', flush=True)
        pause('drive_pause')
        print('[3/6] 직진 재개', flush=True)
        request(True)
        wait_for(lambda: abs(pose.angular_velocity) > 0.5 and pose.linear_velocity == 0)
        print('[4/6] 회전 중 정지', flush=True)
        pause('turn_pause')
        print('[5/6] 회전 재개 → 두 바퀴 주행', flush=True)
        request(True)
        wait_for(lambda: laps >= 2)
        print('[6/6] 두 바퀴 완료 → 최종 정지', flush=True)
        pause('final_pause')
        results['completed_laps'] = laps
        results['package'] = 'mission1_202302200'
        Path('results/patrol_demo_verification.json').write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + '\n')
        print('검증 통과: 사각형 2바퀴 + 직진/회전 정지·재개 + 최종 정지', flush=True)
    finally:
        if client.service_is_ready():
            future = client.call_async(SetBool.Request(data=False))
            rclpy.spin_until_future_complete(node, future, timeout_sec=2)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
