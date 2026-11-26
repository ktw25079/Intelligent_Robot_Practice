#!/usr/bin/env python3
import time

import rclpy
from action_msgs.msg import GoalStatus
from builtin_interfaces.msg import Duration
from control_msgs.action import FollowJointTrajectory, GripperCommand
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from trajectory_msgs.msg import JointTrajectoryPoint

ARM_JOINTS = ['joint1', 'joint2', 'joint3', 'joint4']
POSES = {
    'home':     [0.0, -1.05, 1.05, 0.0],
    'approach': [0.03988350, 0.33440781, 0.03528156, 0.85442730],
    'lower':    [0.05982525, 0.72557291, -0.27765052, 0.94646615],
    'lift':     [0.05062137, 0.59224, -0.42859, 1.24761],
    'transfer': [-0.64427193, 0.59224, -0.42859, 1.24761],
    'place':    [-0.64427193, 0.70256320, -0.21015537, 1.01396130],
    'retreat':  [-0.64427193, 0.60592241, -0.39730102, 1.38518465],
}


class PickDemo(Node):
    def __init__(self):
        super().__init__('re_pick_demo')
        self.arm = ActionClient(self, FollowJointTrajectory,
                                '/arm_controller/follow_joint_trajectory')
        self.grip = ActionClient(self, GripperCommand, '/gripper_controller/gripper_cmd')

    def execute(self, client, goal, label):
        self.get_logger().info(label)
        pending = client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, pending)
        handle = pending.result()
        if not handle.accepted:
            raise RuntimeError(f'{label} 명령 거부')
        result = handle.get_result_async()
        try:
            rclpy.spin_until_future_complete(self, result)
        except KeyboardInterrupt:
            cancel = handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel, timeout_sec=3)
            raise
        response = result.result()
        if response.status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError(f'{label} 중단 — {response.result}')
        return response.result

    def arm_to(self, label, positions, seconds, start=None):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = ARM_JOINTS
        if start is not None:
            ramp = 4
            speed = [(end - begin) / (seconds - ramp) for begin, end in zip(start, positions)]
            first = JointTrajectoryPoint()
            first.positions = start
            first.velocities = [0.0] * 4
            goal.trajectory.points.append(first)
            for sec, angles in [
                (ramp, [a + v * ramp / 2 for a, v in zip(start, speed)]),
                (seconds - ramp, [a - v * ramp / 2 for a, v in zip(positions, speed)]),
            ]:
                waypoint = JointTrajectoryPoint()
                waypoint.positions = angles
                waypoint.velocities = speed
                waypoint.time_from_start = Duration(sec=sec)
                goal.trajectory.points.append(waypoint)
        point = JointTrajectoryPoint()
        point.positions = positions
        point.velocities = [0.0] * 4
        point.time_from_start = Duration(sec=seconds)
        goal.trajectory.points.append(point)
        result = self.execute(self.arm, goal, label)
        if result.error_code != FollowJointTrajectory.Result.SUCCESSFUL:
            raise RuntimeError(f'{label} — {result.error_string}')

    def gripper(self, label, position):
        goal = GripperCommand.Goal()
        goal.command.position = position
        goal.command.max_effort = 5.0
        self.execute(self.grip, goal, label)
        time.sleep(1.0)

    def run(self):
        if not self.arm.wait_for_server(timeout_sec=5) or not self.grip.wait_for_server(timeout_sec=5):
            raise RuntimeError('팔·그리퍼 액션 서버와 브링업 상태를 확인하세요.')
        self.gripper('1. 그리퍼 개방', 0.019)
        self.arm_to('1. A 상공 접근', POSES['approach'], 25, start=POSES['home'])
        time.sleep(1.0)
        self.arm_to('2. A 하강', POSES['lower'], 14)
        self.gripper('3. 파지', 0.0)
        self.arm_to('4. 상승', POSES['lift'], 20)
        self.arm_to('5. B 상공 이송', POSES['transfer'], 19, start=POSES['lift'])
        self.arm_to('6. B 하강', POSES['place'], 16)
        self.gripper('6. B에서 개방', 0.019)
        self.arm_to('6. 상승 후퇴', POSES['retreat'], 11)
        self.arm_to('B 방향에서 팔 접기', [POSES['retreat'][0], *POSES['home'][1:]], 34, start=POSES['retreat'])
        self.arm_to('브링업 복귀', POSES['home'], 11)
        self.get_logger().info('6단계 및 브링업 복귀 완료')


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = PickDemo()
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
