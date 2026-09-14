#!/usr/bin/env python3
"""Publish a numbered greeting on /chatter once per second."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        self.count = 1
        self.timer = self.create_timer(1.0, self.publish_message)

    def publish_message(self):
        message = String()
        message.data = f'Hello World: {self.count}'
        self.publisher.publish(message)
        self.get_logger().info(f"Publishing: '{message.data}'")
        self.count += 1


def main():
    rclpy.init()
    node = Talker()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
