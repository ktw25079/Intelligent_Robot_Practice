"""한 변의 이동 거리와 기준 방향으로 사각형 순찰을 제어한다."""

import math
from enum import Enum, auto


def angle_error(target, current):
    """-pi ~ pi 범위에서 가장 짧은 회전 방향을 구한다."""
    return math.atan2(math.sin(target - current), math.cos(target - current))


def limit(value, maximum):
    return max(-maximum, min(maximum, value))


class Phase(Enum):
    DRIVE = auto()
    TURN = auto()


class SquareMotion:
    DISTANCE_TOLERANCE = 0.01
    ANGLE_TOLERANCE = 0.002

    def __init__(self, side_length, speed, turn_speed):
        self.side_length = side_length
        self.speed = speed
        self.turn_speed = turn_speed
        self.phase = Phase.DRIVE
        self.completed_sides = 0
        self.completed_laps = 0
        self.origin = None
        self.initial_heading = None
        self.heading = None

    def command(self, x, y, theta):
        """현재 pose를 받아 (직진 속도, 회전 속도)를 반환한다."""
        if self.origin is None:
            self.origin = (x, y)
            self.initial_heading = theta
            self.heading = theta

        error = angle_error(self.heading, theta)
        if self.phase == Phase.TURN:
            if abs(error) <= self.ANGLE_TOLERANCE:
                self.origin = (x, y)
                self.phase = Phase.DRIVE
                self.completed_laps = self.completed_sides // 4
                return 0.0, 0.0
            return 0.0, limit(5.0 * error, self.turn_speed)

        # 현재 변의 시작점에서 진행 방향으로 이동한 거리만 측정한다.
        dx, dy = x - self.origin[0], y - self.origin[1]
        traveled = dx * math.cos(self.heading) + dy * math.sin(self.heading)
        remaining = self.side_length - traveled
        if remaining <= self.DISTANCE_TOLERANCE:
            self.completed_sides += 1
            self.phase = Phase.TURN
            # 현재 각도에 90도를 더하면 오차가 누적된다. 첫 방향을 기준으로 삼는다.
            self.heading = self.initial_heading + (self.completed_sides % 4) * math.pi / 2
            return 0.0, 0.0

        # 모서리에 가까워지면 감속하고, 직진 중 방향 오차도 보정한다.
        linear = min(self.speed, 3.0 * remaining) if abs(error) < 0.15 else 0.0
        return linear, limit(5.0 * error, self.turn_speed)
