# demo_2dsim.py
from dataclasses import dataclass
import logging
from time import time, sleep
import math
from math import atan2
from smartbot_irl.robot import SmartBotType
from smartbot_irl.utils import SmartLogger, check_realtime
from smartbot_irl import Command, SensorData, SmartBot
from smartbot_irl.data import State, list_sensor_columns, timestamp
import numpy as np
from student_plotting import setup_plotting
from student_teleop import get_key_command

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    side_length: float = 2.0
    speed: float = 1.0
    turn_speed: float = 0.8
    t0: float = 0.0


# def get_range_forward(scan: LaserScan) -> float:
#     """For coordinate conventions see REP 103 and REP 105:
#     https://www.ros.org/reps/rep-0105.html
#     https://www.ros.org/reps/rep-0103.html
#     Find range directly forward. Scan starts at -2piRAD -> ranges[0].
#     forward_range = (0RAD - 2piRAD) / angle_per_increment)
#     """
#     forward_range = scan.ranges[int((0 * pi - scan.angle_min) / scan.angle_increment)]
#     logger.debug(f'{forward_range=}', rate=1)
#     return forward_range


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


def step(bot: SmartBotType, params: Params, states: State) -> None:
    """This is the main control loop for the robot. Code here should run in <50ms."""

    # Get info about previous timestep state.
    state_prev = states.last
    t_prev = state_prev.t_epoch  # Last timestamp (sec).

    # Create current state vector.
    t = time()
    state_now = {
        't_epoch': t,  # Seconds since Jan 1 1970.
        't_delta': t - t_prev,  # Seconds since last time step.
        't_elapsed': t - params.t0,  # Seconds since program start.
    }

    sensors = bot.read()

    # Do stuff with hex poses if they exist.
    if len(sensors.seen_hexes.poses) > 0:
        logger.info('Adding hex to state')
        hex_x = sensors.seen_hexes.poses[0].x
        hex_y = sensors.seen_hexes.poses[0].y
        hex_yaw = sensors.seen_hexes.poses[0].yaw

        # Add new columns to our state vector (So we can plot!).
        state_now['hex_x'] = hex_x
        state_now['hex_y'] = hex_y
        state_now['hex_yaw'] = hex_yaw

    # Do stuff odom data.
    state_now['odom_x'] = sensors.odom.x
    state_now['odom_y'] = sensors.odom.y
    state_now['odom_yaw'] = sensors.odom.yaw

    # Get a populated Command object from our controller function.
    cmd = ant_controller(sensors)

    # Place a new hex if we are close enough (Only for simulator!)
    if sensors.seen_hexes and sensors.seen_hexes.poses:
        marker = sensors.seen_hexes.poses[0]
        dist = math.hypot(marker.x, marker.y)
        if dist < 0.25:
            bot.place_hex()

    # Send our populated command to the robot.
    bot.write(cmd)

    # Update our `states` matrix by inserting our `state_now` vector.
    states.append_row(rowdict=state_now)
    logger.info(f'\nState (t={state_now["t_elapsed"]}): {state_now}')


def main(log_file='smartlog') -> None:
    """Connect to smartbot, setup plots, save data. Then loop `step()` forever.

    Switch between the real and simulated robot here. Don't forget to make sure
    the IP and smartbot_num match!

    Parameters
    ----------
    log_file : str, optional
        Filename to save data as a CSV, by default 'smartlog'
    """

    logger.info('Connecting to smartbot...')

    # bot = SmartBot(mode='real', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=7)
    bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=7)
    bot.init(host='192.168.33.7', port=9090)

    # Create empty parameter and state objects.
    states = State()  # This gets saved to a CSV.
    params = Params()  # We can access this later in step().
    params.t0 = time()  # Record start time for this run (sec).

    # Print out what columns exist (There may be more added later!)
    logger.info(msg=f'State Columns: {list_sensor_columns()}')

    # Set up plotting.
    plot_manager = setup_plotting()
    plot_manager.start_plot_proc()

    try:
        while True:
            step(bot, params, states)  # Run our code.
            check_realtime(start_t=time())  # Check if our step() is taking too long.
            bot.spin()  # Get new sensor data.

            get_key_command()  # Need this to process quit keypresses.

            bot.spin()  # Get new sensor data.

            # Send last row of data to plots.
            plot_manager.update_queue(states.iloc[-1])

    except KeyboardInterrupt:
        logger.info(msg='Shutting down...')
    finally:
        # Save data to a CSV file and cleanup ros+matplotlib objects.
        log_filename = f'{log_file}_{timestamp()}.csv'
        states.to_csv(log_filename)
        logger.info(f'Done saving to {log_filename}')
        plot_manager.stop_plot_proc()

        # Stop robot driving away.
        cmd = Command(wheel_vel_left=0.0, wheel_vel_right=0.0, linear_vel=0.0, angular_vel=0.0)
        bot.write(cmd)
        sleep(0.3)
        bot.shutdown()


if __name__ == '__main__':
    main()
