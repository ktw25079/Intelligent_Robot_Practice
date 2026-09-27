"""ROS 2 토픽·서비스와 사각 순찰 제어기를 연결하는 노드."""

import math
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_srvs.srv import SetBool
from turtlesim.msg import Pose

from mission1_202302200.square_motion import SquareMotion


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')
        self.declare_parameters('', [
            ('side_length', 3.0), ('speed', 2.0),
            ('turn_speed', 3.0), ('autostart', False),
        ])
        values = [float(self.get_parameter(name).value)
                  for name in ('side_length', 'speed', 'turn_speed')]
        if not all(math.isfinite(value) and value > 0 for value in values):
            raise ValueError('side_length, speed, turn_speed must be positive and finite')
        self.motion = SquareMotion(*values)
        self.enabled = self.get_parameter('autostart').value
        self.pose = None
        self.pose_received_at = 0.0
        self.route_checked = False
        self.route_valid = False
        self.velocity = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.receive_pose, 10)
        self.create_service(SetBool, '/start_stop', self.set_running)
        self.create_timer(0.02, self.control_step)
        self.get_logger().info('Ready: /start_stop (true: start, false: stop)')

    def receive_pose(self, pose):
        self.pose = pose
        self.pose_received_at = time.monotonic()
        if self.route_checked:
            return
        # 처음 받은 위치·방향에서 사각형이 화면 내부에 들어가는지 검사한다.
        x, y = pose.x, pose.y
        corners = [(x, y)]
        for side in range(4):
            heading = pose.theta + side * math.pi / 2
            x += self.motion.side_length * math.cos(heading)
            y += self.motion.side_length * math.sin(heading)
            corners.append((x, y))
        self.route_valid = all(0.2 < x < 10.8 and 0.2 < y < 10.8 for x, y in corners)
        self.route_checked = True
        if self.route_valid:
            # 서비스 대기 중에는 출발 기준점이 바뀌지 않도록 여기서 초기화한다.
            self.motion.command(pose.x, pose.y, pose.theta)
        else:
            self.enabled = False
            self.get_logger().error('Square is outside the window; reduce side_length and restart')

    def pose_is_fresh(self):
        return self.pose is not None and time.monotonic() - self.pose_received_at <= 0.5

    def publish_velocity(self, linear=0.0, angular=0.0):
        message = Twist()
        message.linear.x = linear
        message.angular.z = angular
        self.velocity.publish(message)

    def set_running(self, request, response):
        if request.data and (not self.route_valid or not self.pose_is_fresh()):
            response.success = False
            response.message = 'Cannot start: fresh pose and a valid square are required'
            return response
        self.enabled = request.data
        if not self.enabled:
            self.publish_velocity()
        response.success = True
        response.message = 'Patrol resumed' if self.enabled else 'Paused; current side and phase retained'
        self.get_logger().info(response.message)
        return response

    def control_step(self):
        if not self.enabled or not self.route_valid or not self.pose_is_fresh():
            self.publish_velocity()
            return
        previous_sides = self.motion.completed_sides
        previous_laps = self.motion.completed_laps
        command = self.motion.command(self.pose.x, self.pose.y, self.pose.theta)
        self.publish_velocity(*command)
        if self.motion.completed_sides != previous_sides:
            corner = (self.motion.completed_sides - 1) % 4 + 1
            self.get_logger().info(f'Corner {corner}/4: turning 90 degrees')
        if self.motion.completed_laps != previous_laps:
            self.get_logger().info(f'Lap {self.motion.completed_laps} complete')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = Patrol()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            if rclpy.ok():
                node.publish_velocity()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
