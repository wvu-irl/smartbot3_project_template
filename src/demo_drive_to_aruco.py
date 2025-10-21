# demo_2dsim.py
import logging
import time
import math
from math import pi, atan2
from smartbot_irl.robot import SmartBotType
from smartbot_irl.utils import SmartLogger
from smartbot_irl import Command, SensorData, SmartBot
from smartbot_irl.robot.smartbot_base import SmartBotBase
from smartbot_irl.data import LaserScan
from teleop import get_key_command

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


def get_range_forward(scan: LaserScan) -> float:
    """For coordinate conventions see REP 103 and REP 105:
    https://www.ros.org/reps/rep-0105.html
    https://www.ros.org/reps/rep-0103.html
    Find range directly forward. Scan starts at -2piRAD -> ranges[0].
    forward_range = (0RAD - 2piRAD) / angle_per_increment)
    """
    forward_range = scan.ranges[int((0 * pi - scan.angle_min) / scan.angle_increment)]
    logger.debug(f"{forward_range=}", rate=1)
    return forward_range

def ant_controller(sensors, k_goal=2.0, k_avoid=5.5, base_speed=.4, avoid_thresh=1) -> Command:
    """
    Differential-drive 'ant' controller:
      - Steer toward ArUco marker
      - Repel from nearby obstacles
      - Never stop moving forward unless cornered
    """
    cmd = Command()
    scan: LaserScan = sensors.scan
    if scan is None or not scan.ranges:
        return cmd  # do nothing until we have LIDAR

    # ------------------------------
    # 1. Compute goal attraction
    # ------------------------------
    goal_ang = 0.0
    dist_to_goal = None
    if sensors.seen_hexes and sensors.seen_hexes.poses:
        marker = sensors.seen_hexes.poses[0]
        goal_ang = atan2(marker.x, marker.y)
        dist_to_goal = math.hypot(marker.x, marker.y)

    # ------------------------------
    # 2. Compute obstacle repulsion
    # ------------------------------
    n = len(scan.ranges)
    sector_width = n // 36  # 10-degree bins
    repulse = 0.0
    pressure = 0.0

    for i, r in enumerate(scan.ranges):
        if not r or math.isnan(r) or math.isinf(r):
            continue
        if r < avoid_thresh:
            # angle relative to robot heading
            ang = scan.angle_min + i * scan.angle_increment
            w = 1.0 / max(r, 0.05)  # closer obstacles weigh stronger
            repulse -= math.sin(ang) * w  # steer away from obstacle side
            pressure += w

    # Normalize repulsion
    if pressure > 0:
        repulse /= pressure



    # 3. Combine goal + avoidance
    ang_vel = 0.0
    if dist_to_goal is not None:
        ang_vel += k_goal * goal_ang  * 0.3
    if pressure > 0:
        ang_vel += k_avoid * repulse * 0.3

    # Dampen rotation if no goal is visible
    if dist_to_goal is None:
        ang_vel *= 0.2

    # Small deadband to prevent micro-spins
    if abs(ang_vel) < 0.05:
        ang_vel = 0.0

    ang_vel = max(-7, min(7, ang_vel))

    slowdown = 1.0
    decay_rate=2.0
    if dist_to_goal is not None:
        slowdown = 1.0 - math.exp(-decay_rate * dist_to_goal)
    slowdown = max(0.05, slowdown)  # don’t go to zero unless at goal

    v_scale = (1.0 / (1.0 + 0.1 * pressure)) * slowdown
    lin_vel = base_speed * v_scale

    # Stop if we’re basically on top of the goal
    if dist_to_goal and dist_to_goal < 0.25:
        lin_vel = 0.0

    if dist_to_goal is not None and abs(goal_ang) > 0.1:
        cmd.linear_vel = 0.0
    else:
        cmd.angular_vel = 0.0

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


if __name__ == "__main__":
    """ Create an instance of the SmartBot wrapper class for your specific
    smartbot. Then we run our control loop :meth:`step` forever until stopped
    (e.g. <Ctrl-c>)."""

    logger.info("Connecting to smartbot...")
    # bot = SmartBot(mode="real", drawing=True, smartbot_num=0)
    # bot.init(host="localhost", port=9090, yaml_path="default_conf.yml")

    bot = SmartBot(mode="real", drawing=True, smartbot_num=2)
    bot.init(host="192.168.33.2", port=9090, yaml_path="default_conf.yml")

    # bot = SmartBot(mode="sim", drawing=True, smartbot_num=3)
    # bot.init(drawing=True, smartbot_num=3)

    try:
        while True:
            t_start = time.perf_counter()
            step(bot)  # Run your code.

            dt = time.perf_counter() - t_start  # Check if your code is running fast enough.
            if dt > 0.05:
                logger.warn(f"Loop took {dt:2f}s!", rate=1)

            bot.spin()  # Get new sensor data.
    except KeyboardInterrupt:
        print("Shutting down...")
        bot.shutdown()
