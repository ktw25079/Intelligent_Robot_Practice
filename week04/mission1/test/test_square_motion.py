"""ROS 없이 운동학 모형으로 주행 궤적과 상태 전환을 검증한다."""

import math
import unittest

from mission1.square_motion import Phase, SquareMotion, angle_error


class SquareMotionTest(unittest.TestCase):
    def test_repeated_square_and_wrapped_heading(self):
        for initial_heading in (0.0, 2.9, -2.9):
            with self.subTest(initial_heading=initial_heading):
                motion = SquareMotion(3.0, 2.0, 3.0)
                x, y, theta = 0.0, 0.0, initial_heading
                corners = []
                for step in range(20000):
                    old_sides = motion.completed_sides
                    linear, angular = motion.command(x, y, theta)
                    if motion.phase == Phase.TURN:
                        self.assertEqual(linear, 0.0)
                    self.assertLessEqual(abs(linear), 2.0)
                    self.assertLessEqual(abs(angular), 3.0)
                    if motion.completed_sides != old_sides:
                        corners.append((x, y))
                    dt = (0.015, 0.020, 0.025)[step % 3]
                    x += linear * math.cos(theta) * dt
                    y += linear * math.sin(theta) * dt
                    theta = angle_error(theta + angular * dt, 0.0)
                    if motion.completed_laps == 3:
                        break
                self.assertEqual(motion.completed_laps, 3)
                self.assertEqual(len(corners), 12)
                self.assertLess(math.hypot(x, y), 0.08)
                self.assertLess(abs(angle_error(initial_heading, theta)), 0.003)
                for previous, current in zip([(0, 0)] + corners, corners):
                    self.assertAlmostEqual(math.dist(previous, current), 3.0, delta=0.025)

    def test_partial_side_is_not_restarted(self):
        motion = SquareMotion(3.0, 2.0, 3.0)
        motion.command(0.0, 0.0, 0.0)
        motion.command(1.5, 0.0, 0.0)
        # 정지 동안 제어기를 호출하지 않고, 같은 위치에서 재개한다.
        linear, angular = motion.command(1.5, 0.0, 0.0)
        self.assertGreater(linear, 0.0)
        self.assertEqual(motion.origin, (0.0, 0.0))
        motion.command(3.0, 0.0, 0.0)
        self.assertEqual(motion.phase, Phase.TURN)
        self.assertEqual(motion.completed_sides, 1)


if __name__ == '__main__':
    unittest.main()
