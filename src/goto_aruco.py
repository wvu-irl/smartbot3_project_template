# demo_2dsim.py
import logging
import time
import math
from math import pi, atan2
from smartbot_irl.robot import SmartBotType
from smartbot_irl.utils import SmartLogger
from smartbot_irl import Command, SensorData, SmartBot
from smartbot_irl.data import LaserScan
import numpy as np
from student_teleop import get_key_command

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


def get_range_forward(scan: LaserScan) -> float:
    """For coordinate conventions see REP 103 and REP 105:
    https://www.ros.org/reps/rep-0105.html
    https://www.ros.org/reps/rep-0103.html
    Find range directly forward. Scan starts at -2piRAD -> ranges[0].
    forward_range = (0RAD - 2piRAD) / angle_per_increment)
    """
    forward_range = scan.ranges[int((0 * pi - scan.angle_min) / scan.angle_increment)]
    logger.debug(f'{forward_range=}', rate=1)
    return forward_range


def ant_controller(
    sensors: SensorData,
    k_goal=2.0,
    k_avoid=0.0,
    base_speed=0.3,
    avoid_thresh=0.5,
) -> Command:
    """
    Drive towards any visible hexes while avoiding obstacles.

    Parameters
    ----------
    k_goal: float, default=0.2
    k_avoid: float, default=2.0
    base_speed:float, default=0.3
    avoid_thresh:float, default=0.5
        Range at which we consider something to be an obstacle (m)
    """
    cmd = Command()
    scan = sensors.scan

    # Do nothing until we have LIDAR.
    if scan is None or not scan.ranges:
        return cmd

    goal_ang = 0.0
    dist_to_goal = None

    # Check if there are any hexes visible.
    if sensors.seen_hexes and sensors.seen_hexes.poses:
        # Grab the first one we see (lowest marker_id?).
        marker = sensors.seen_hexes.poses[0]
        logger.info(marker, rate=1)

        goal_ang = atan2(marker.y, marker.x)
        dist_to_goal = math.hypot(marker.x, marker.y)

    # Use only a forward chunk of the lidar ranges.
    ranges = np.array(scan.ranges, dtype=float)  # Make a numpy array for convenience.
    n = len(ranges)

    front_width = np.deg2rad(120)  # +/-60
    half = front_width / 2

    angle_min = scan.angle_min
    angle_inc = scan.angle_increment

    # If a given range's angle is outside the span make it a NaN.
    for i in range(n):
        ang = angle_min + i * angle_inc
        if ang < -half or ang > half:
            ranges[i] = np.nan

    scan.ranges = ranges.tolist()  # Back to a list type.

    repulse = 0.0
    pressure = 0.0

    for i, r in enumerate(scan.ranges):
        if not r or math.isnan(r) or math.isinf(r):
            continue
        if r < avoid_thresh:
            # angle relative to robot heading
            ang = scan.angle_min + i * scan.angle_increment
            w = 1.0 / max(r, 0.05)  # Closer obstacles cause more repulsion.
            repulse -= math.sin(ang) * w  # Steer away from that ranges heading.
            pressure += w  # How much confined the robot is.

    # Normalize repulsion
    if pressure > 0:
        repulse /= pressure

    # Combine turning towards marker and away from obstacles.
    ang_vel = 0.0
    if dist_to_goal is not None:
        ang_vel += k_goal * goal_ang * 0.3
    if pressure > 0:
        ang_vel += k_avoid * repulse * 0.3

    # Rotate less aggressively if we can't see a marker.
    if dist_to_goal is None:
        ang_vel *= 0.8

    if abs(ang_vel) < 0.05:
        ang_vel = 0.0

    ang_vel = max(-4, min(4, ang_vel))

    # Slow down as we get nearer.
    slowdown = 1.0
    decay_rate = 2.0
    if dist_to_goal is not None:
        slowdown = 1.0 - math.exp(-decay_rate * dist_to_goal)
    slowdown = max(0.05, slowdown)

    v_scale = (1.0 / (1.0 + 0.1 * pressure)) * slowdown
    lin_vel = base_speed * v_scale

    # Stop if we’re basically on top of the goal.
    if dist_to_goal and dist_to_goal < 0.15:
        lin_vel = 0.0

    # Rotate in place before we start driving.
    if dist_to_goal is not None and abs(goal_ang) > 0.3:
        lin_vel = 0.0

    cmd.linear_vel = lin_vel
    cmd.angular_vel = ang_vel
    return cmd


def step(bot: SmartBotType):
    """Drive to nearest aruco marker"""
    sensors = bot.read()
    cmd = Command()

    cmd = ant_controller(sensors)

    if sensors.seen_hexes and sensors.seen_hexes.poses:
        marker = sensors.seen_hexes.poses[0]
        dist = math.hypot(marker.x, marker.y)
        if dist < 0.25:
            bot.place_hex()

    bot.write(cmd)


if __name__ == '__main__':
    """ Create an instance of the SmartBot wrapper class for your specific
    smartbot. Then we run our control loop :meth:`step` forever until stopped
    (e.g. <Ctrl-c>)."""

    logger.info('Connecting to smartbot...')

    # bot = SmartBot(mode='real', drawing=True, smartbot_num=3)
    bot = SmartBot(mode='sim', drawing=True, smartbot_num=7)
    bot.init(host='192.168.33.7', port=9090)

    # bot.init(drawing=True, smartbot_num=3)

    try:
        while True:
            t_start = time.perf_counter()
            step(bot)  # Run your code.
            get_key_command()

            dt = time.perf_counter() - t_start  # Check if your code is running fast enough.
            if dt > 0.05:
                logger.warn(msg=f'Loop took {dt:2f}s!', rate=1)

            bot.spin()  # Get new sensor data.

    except KeyboardInterrupt:
        logger.info(msg='Shutting down...')
    finally:
        cmd = Command(wheel_vel_left=0.0, wheel_vel_right=0.0, linear_vel=0.0, angular_vel=0.0)
        bot.write(cmd)
        time.sleep(0.3)
        bot.shutdown()
