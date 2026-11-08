#!/usr/bin/env python3
"""Display a ROS USB-camera stream and ArUco IDs without uncalibrated pose estimates."""
import argparse
import time
import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', default='/logitech/image_raw')
    args = parser.parse_args()
    rclpy.init(args=[])
    node = rclpy.create_node('logitech_viewer')
    bridge = CvBridge()
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(dictionary) if hasattr(cv2.aruco, 'ArucoDetector') else None
    state = {'frame': None, 'count': 0, 'ids': [], 'start': None, 'last': 0.0}
    def on_image(msg):
        now = time.monotonic()
        if state['start'] is None:
            state['start'] = now
            print(f'FIRST_FRAME {msg.width}x{msg.height} encoding={msg.encoding}', flush=True)
        frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray) if detector else cv2.aruco.detectMarkers(gray, dictionary)
        found = [] if ids is None else ids.ravel().tolist()
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        if found != state['ids']:
            print(f'ArUco IDs: {found}', flush=True)
        state.update(frame=frame, ids=found, last=now, count=state['count']+1)
    sub = node.create_subscription(Image, args.topic, on_image, qos_profile_sensor_data)
    title = 'Logitech C920 - LIVE - ArUco ID check'
    cv2.namedWindow(title, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title, 960, 720)
    last_report = time.monotonic()
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.05)
            now = time.monotonic()
            frame = state['frame']
            view = np.zeros((480, 640, 3), np.uint8) if frame is None else cv2.resize(frame, (640, 480))
            stale = frame is None or now-state['last'] > 3
            label = 'Waiting for frames...' if stale else f"LIVE | frames: {state['count']} | IDs: {state['ids']}"
            cv2.putText(view, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
            cv2.imshow(title, view)
            if cv2.waitKey(1) & 0xff in (27, ord('q')):
                break
            if now-last_report >= 10:
                print(f"received={state['count']} last_frame_age={now-state['last']:.2f}s ids={state['ids']}", flush=True)
                last_report = now
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
