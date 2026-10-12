#!/usr/bin/env python3
"""Base-only keyboard teleop, with the lecture's i/k/j/l/space controls.
Publishes real Twist commands; Gazebo generates all sensor/odometry data.
"""
import os, select, sys, termios, tty
import rclpy
from geometry_msgs.msg import Twist

def main():
    rclpy.init()
    node=rclpy.create_node('lecture06_keyboard_teleop')
    pub=node.create_publisher(Twist,'/cmd_vel',10)
    command=Twist()
    old=termios.tcgetattr(sys.stdin)
    print('i/k: linear +/-0.01 m/s | j/l: angular +/-0.1 rad/s | SPACE: stop | ESC: quit',flush=True)
    tty.setcbreak(sys.stdin)
    try:
        while rclpy.ok():
            if select.select([sys.stdin],[],[],0.1)[0]:
                key=os.read(sys.stdin.fileno(),1).decode()
                if key=='\x1b': break
                if key=='i': command.linear.x=min(.2,command.linear.x+.01)
                elif key=='k': command.linear.x=max(-.2,command.linear.x-.01)
                elif key=='j': command.angular.z=min(.5,command.angular.z+.1)
                elif key=='l': command.angular.z=max(-.5,command.angular.z-.1)
                elif key==' ': command=Twist()
                print(f'linear.x={command.linear.x:.2f}, angular.z={command.angular.z:.2f}',flush=True)
            pub.publish(command)
    finally:
        for _ in range(5): pub.publish(Twist())
        termios.tcsetattr(sys.stdin,termios.TCSADRAIN,old)
        node.destroy_node();rclpy.shutdown()
if __name__=='__main__': main()
