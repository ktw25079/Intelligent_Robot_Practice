"""Mission 3: verify plans without motion; --execute sends A then B.

Adapted from the lecture go_to_pose.py (Apache-2.0).
Actual obstacle avoidance/collision-free operation requires video review.
"""
import argparse
import json
import math
import signal
import time
from datetime import datetime, timezone
from pathlib import Path


def read_goals(path):
    data = json.loads(Path(path).read_text())
    for name in ('A', 'B'):
        for key in ('x', 'y', 'yaw'):
            if not math.isfinite(float(data[name][key])):
                raise ValueError(f'Invalid {name}.{key}')
    if float(data.get('goal_timeout_sec', 180)) <= 0:
        raise ValueError('Timeout must be positive')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--goals', required=True)
    parser.add_argument('--log', required=True)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--initial-pose', help='Verified map x/y/yaw JSON; never assume origin')
    args = parser.parse_args()
    config = read_goals(args.goals)
    import rclpy
    from geometry_msgs.msg import PoseStamped
    from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
    from nav_msgs.msg import Path as NavPath
    from nav_msgs.msg import Odometry
    from rclpy.qos import qos_profile_sensor_data
    from rclpy.signals import SignalHandlerOptions
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    def interrupt(signum, frame):
        raise KeyboardInterrupt(f'Signal {signum}')
    signal.signal(signal.SIGINT, interrupt)
    signal.signal(signal.SIGTERM, interrupt)
    nav = BasicNavigator()
    logpath = Path(args.log)
    logpath.parent.mkdir(parents=True, exist_ok=True)
    output = logpath.open('x', buffering=1)
    running = False
    odom_state = {'last': None, 'received': 0.0, 'error': None}

    def log(event, **values):
        row = {'utc': datetime.now(timezone.utc).isoformat(), 'event': event, **values}
        output.write(json.dumps(row) + '\n')
        if event != 'planner_path':
            print(json.dumps(row, ensure_ascii=False), flush=True)

    def pose(values):
        p = PoseStamped()
        p.header.frame_id = 'map'
        p.header.stamp = nav.get_clock().now().to_msg()
        p.pose.position.x, p.pose.position.y = float(values['x']), float(values['y'])
        p.pose.orientation.z = math.sin(values['yaw'] / 2)
        p.pose.orientation.w = math.cos(values['yaw'] / 2)
        return p

    # Changes also occur during ordinary replanning: this is supporting data,
    # never automatic proof of obstacle avoidance or collision-free motion.
    subscription = nav.create_subscription(NavPath, '/plan', lambda msg: log(
        'planner_path', points=[[p.pose.position.x, p.pose.position.y]
                                for p in msg.poses]), 10)
    def check_odom(msg):
        p = msg.pose.pose.position
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec / 1e9
        age = nav.get_clock().now().nanoseconds / 1e9 - stamp
        if not all(math.isfinite(v) for v in (p.x, p.y, age)):
            odom_state['error'] = 'Non-finite odometry'
        elif abs(p.x) > 100 or abs(p.y) > 100:
            odom_state['error'] = 'Odometry outside classroom-scale bounds'
        elif abs(age) > 3:
            odom_state['error'] = 'Stale odometry / clocks not aligned'
        previous = odom_state['last']
        if previous:
            dt = stamp - previous[2]
            distance = math.hypot(p.x - previous[0], p.y - previous[1])
            if dt < 0 or distance > max(.2, max(dt, 0) * .4):
                odom_state['error'] = 'Odometry discontinuity'
        odom_state['last'] = (p.x, p.y, stamp)
        odom_state['received'] = time.monotonic()
    odom_subscription = nav.create_subscription(
        Odometry, '/odom', check_odom, qos_profile_sensor_data)

    def require_odom():
        if odom_state['error']:
            raise RuntimeError(odom_state['error'])
        if time.monotonic() - odom_state['received'] > 3:
            raise RuntimeError('No fresh odometry')
    try:
        log('session', execute=args.execute, goals=config)
        if args.initial_pose:
            initial = pose(json.loads(Path(args.initial_pose).read_text()))
            initial.header.stamp.sec = 0
            initial.header.stamp.nanosec = 0
            nav.setInitialPose(initial)
        else:
            # Humble BasicNavigator otherwise republishes its default (0,0,0)
            # before a delayed AMCL sample arrives. Never silently relocate.
            deadline = time.monotonic() + 15
            while not nav.initial_pose_received and time.monotonic() < deadline:
                rclpy.spin_once(nav, timeout_sec=.1)
            if not nav.initial_pose_received:
                raise RuntimeError('No AMCL pose; provide verified --initial-pose')
        nav.waitUntilNav2Active()
        deadline = time.monotonic() + 10
        while odom_state['last'] is None and time.monotonic() < deadline:
            rclpy.spin_once(nav, timeout_sec=.1)
        require_odom()
        if not args.execute:
            path = nav.getPath(pose(config['A']), pose(config['B']), use_start=True)
            if path is None or not path.poses:
                raise RuntimeError('No path from A to B')
            log('plan_verified_no_motion', points=[
                [p.pose.position.x, p.pose.position.y] for p in path.poses])
            return
        for name in ('A', 'B'):
            log('goal_sent', goal=name)
            if not nav.goToPose(pose(config[name])):
                raise RuntimeError(f'{name}: goal rejected')
            running = True
            started, last = time.monotonic(), 0.0
            while not nav.isTaskComplete():
                require_odom()
                now = time.monotonic()
                if now - started > config.get('goal_timeout_sec', 180):
                    nav.cancelTask()
                    running = False
                    raise RuntimeError(f'{name}: timeout; canceled')
                feedback = nav.getFeedback()
                if feedback and now - last >= 1:
                    log('feedback', goal=name, distance=feedback.distance_remaining,
                        recoveries=feedback.number_of_recoveries)
                    last = now
                time.sleep(0.05)
            running = False
            result = nav.getResult()
            log('goal_result', goal=name, result=str(result))
            if result != TaskResult.SUCCEEDED:
                raise RuntimeError(f'{name} did not succeed; no next goal sent')
        log('sequence_succeeded', video_review_required=True)
    except BaseException as exc:
        if running:
            nav.cancelTask()
        log('stopped', reason=str(exc))
        raise
    finally:
        nav.destroy_subscription(subscription)
        nav.destroy_subscription(odom_subscription)
        nav.destroy_node()
        rclpy.shutdown()
        output.close()


if __name__ == '__main__':
    main()
