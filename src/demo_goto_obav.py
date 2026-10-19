# steer_to_waypoint.py, here robot steers to waypoint adjusting the linear and rotational error.
import math
from dataclasses import dataclass
from random import random
from time import time

import numpy as np
from numpy import linspace
from smartbot_irl.data import State, list_sensor_columns, timestamp
from smartbot_irl.utils import SmartLogger, check_realtime, logging

from smartbot_irl import Command, SmartBot, SmartBotType
from student_dwa import dynamic_window_planner
from student_plotting import setup_plotting

logger = SmartLogger(level=logging.WARN)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    linear_gain = 1
    rotational_gain = 2
    goal_x: float = 0.0
    goal_y: float = 0.0
    heading_tol: float = 0.01  # rad (~0.5 deg) -- how close is "facing the waypoint"
    distance_tol: float = 0.1  # m -- how close is "at the waypoint"

    goal_timeout = 30.0  # max time to reach goal in seconds
    start_time = 0.0  # When was this goal chosen? (s)


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

    # Get sensor data.
    sensors = bot.read()

    # Do stuff with IMU data.
    logger.debug(sensors.imu)
    ax = sensors.imu.ax
    ay = sensors.imu.ay
    az = sensors.imu.az
    wz = sensors.imu.wz

    # Add new columns to our state vector.
    state_now['imu_ax'] = ax
    state_now['imu_ay'] = ay
    state_now['imu_az'] = az
    state_now['imu_wz'] = wz

    # Do stuff odom data.
    state_now['odom_x'] = sensors.odom.x
    state_now['odom_y'] = sensors.odom.y
    state_now['odom_yaw'] = sensors.odom.yaw

    ###########################
    #   Goal Choosing Stuff   #
    ###########################

    # Have we timed out of the goal?
    if params.start_time + params.goal_timeout < t:
        print('Could not reach goal in time, choosing new goal')

        # Choose a new goal in a 2m radius
        theta = 2 * math.pi * random()
        radius = math.sqrt(random())

        delta_x = radius * math.cos(theta)
        delta_y = radius * math.sin(theta)

        params.goal_x = sensors.odom.x + delta_x
        params.goal_y = sensors.odom.y + delta_y
        params.start_time = t

        print(f'New Goal Selected: ({params.goal_x},{params.goal_y})')

    ##########################
    #   Obstacle Avoidance   #
    ##########################

    # Get the LiDar Data
    lidar_ranges = np.array(sensors.scan.ranges).astype(float)
    lidar_angles = linspace(sensors.scan.angle_min, sensors.scan.angle_max, len(lidar_ranges))

    # Clean it up a bit
    MAX_LIDAR_RANGE = 10.0

    # We only care about max, min is handled by the dwa planner
    if len(lidar_ranges) > 0:
        valid_points = np.isfinite(lidar_ranges) & (lidar_ranges <= MAX_LIDAR_RANGE)

        lidar_ranges = lidar_ranges[valid_points]
        lidar_angles = lidar_angles[valid_points]

    # Get Distance and Heading Errors
    goal_dx = params.goal_x - sensors.odom.x
    goal_dy = params.goal_y - sensors.odom.y

    # Calculate Distance to Goal
    goal_dist = np.sqrt(goal_dx**2 + goal_dy**2)
    print(f'distance to the goal is {goal_dist}')

    # Calculate Heading Error
    desired_heading = math.atan2(goal_dy, goal_dx)
    raw_heading_error = desired_heading - sensors.odom.yaw
    heading_error = math.atan2(math.sin(raw_heading_error), math.cos(raw_heading_error))
    print(f'heading error is  {heading_error}')

    # If we are at the goal
    if goal_dist < params.distance_tol:
        lin_vel = 0.0
        ang_vel = 0.0
        print('Reached goal point!')

        # Choose a new goal in a 2m radius
        theta = 2 * math.pi * random()
        radius = math.sqrt(random())

        delta_x = radius * math.cos(theta)
        delta_y = radius * math.sin(theta)

        params.goal_x = sensors.odom.x + delta_x
        params.goal_y = sensors.odom.y + delta_y
        params.start_time = t

        print(f'New Goal Selected: ({params.goal_x},{params.goal_y})')

    # If there is no lidar data, or if all things are super far away, just move w/ a P controller
    elif len(lidar_ranges) == 0 or min(lidar_ranges) > 0.45:
        if goal_dist > params.distance_tol:
            lin_vel = params.linear_gain * goal_dist

        if abs(heading_error) > params.heading_tol:
            ang_vel = params.rotational_gain * heading_error

    # If we aren't at the goal, and we have lidar data, and there are things close
    else:
        lin_vel, ang_vel = dynamic_window_planner(
            lidar_ranges=lidar_ranges,
            lidar_angles=lidar_angles,
            odom=sensors.odom,
            goal_point=(params.goal_x, params.goal_y),
        )

    # Write output to Command
    cmd = Command(linear_vel=lin_vel, angular_vel=ang_vel)
    bot.write(cmd)

    # Update our `states` matrix by inserting our `state_now` vector.
    # state_now.update(sensors.flatten())
    states.append_row(rowdict=state_now)
    logger.info(f'\nState (t={state_now["t_elapsed"]}): {state_now}')


def main(log_file='gyro_relog') -> None:
    """Connect to smartbot, setup plots, save data. Then loop `step()` forever.

    Switch between the real and simulated robot here. Don't forget to make sure
    the IP and smartbot_num match!

    Parameters
    ----------
    log_file : str, optional
        Filename to save data as a CSV, by default 'smartlog'
    """

    #######################
    #   Robot Selection   #
    #######################

    # Connect to a real robot.
    bot = SmartBot(mode='real', drawing=True, smartbot_num=7)
    bot.init(host='192.168.33.7', port=9090, yaml_path='default_conf.yml')

    # Connect to a sim robot.
    logger.info('Connecting to smartbot...')
    # bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    # bot.init(drawing=True, smartbot_num=3)

    # Create empty parameter and state objects.
    states = State()  # This gets saved to a CSV.
    params = Params()  # We can access this later in step().
    params.t0 = time()  # Record start time for this run (sec).

    # for resseting the origin
    bot.write(cmd=Command(reset_position=True))

    # Set up plotting.
    plot_manager = setup_plotting()
    plot_manager.start_plot_proc()

    # Print out what columns exist (There may be more added later!)
    logger.info(msg=f'State Columns: {list_sensor_columns()}')

    # Run the robot!
    #######################################
    try:
        while True:
            step(bot, params, states)  # Run our code.
            check_realtime(start_t=time())  # Check if our step() is taking too long.
            bot.spin()  # Get new sensor data.

            # Send last row of data to plots.
            plot_manager.update_queue(states.iloc[-1])

    except KeyboardInterrupt:
        logger.info('User requesting shut down...')
    finally:
        # Save data to a CSV file and cleanup ros+matplotlib objects.
        log_filename = f'{log_file}_{timestamp()}.csv'
        states.to_csv(log_filename)
        # logger.info(f'Done saving to {log_filename}')
        plot_manager.stop_plot_proc()

        bot.shutdown()


if __name__ == '__main__':
    main()
