# demo_2dsim.py
from dataclasses import dataclass
from math import cos, inf, pi, sin, sqrt
import math
import random
from time import sleep, time
from types import SimpleNamespace
from typing import Optional, TypedDict

from smartbot_irl import Command, sim2d, SmartBot, SmartBotType
from smartbot_irl.data import (
    IMU,
    ArucoMarkers,
    JointState,
    LaserScan,
    PoseArray,
    States,
    String,
    list_sensor_columns,
    timestamp,
)
from smartbot_irl.data._type_maps import Odometry
from smartbot_irl.utils import SmartLogger, check_realtime, logging, get_log_dir, save_data

from student_plotting import setup_plotting
from student_teleop import get_key

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    side_length: float = 2.0
    speed: float = 2.0
    turn_speed: float = 2.0
    t0: float = 0.0
    controller_rate: float = 50.0
    log_filename: Optional[str] = None
    p: float = 1
    i: float = 0.0
    d: float = 0.0


"""This tracks the current state. Get's inserted into states matrix each step.
We can add additional entries whenever we please.
"""
state = SimpleNamespace(
    t_delta=0.0,
    t_elapsed=0.0,
    t_epoch=0.0,
    x=0.0,
    y=0.0,
    mode='searching',  # searching, goto, arrived
    nearest_hex_id=0,
    nearest_hex_x=0,
    nearest_hex_y=0,
    goal_x=0.0,
    goal_y=0.0,
    heading=0.0,
    target_heading=0.0,
)


def step(bot: SmartBotType, params: Params, states: States) -> None:
    """This is the main control loop for the robot. Code here should run in <50ms."""

    # Get info about previous timestep state.
    state_prev = states.last
    t_prev = state_prev.t_epoch  # Last timestamp (sec).

    # Create current state vector.
    t = time()
    state.t_epoch = t
    state.t_delta = t - t_prev
    state.t_elapsed = t - params.t0

    # Get sensor data.
    sensors = bot.read()

    # Do stuff with IMU data.
    logger.debug(sensors.imu)
    state.imu_ax = sensors.imu.ax
    state.imu_ay = sensors.imu.ay
    state.imu_az = sensors.imu.az
    state.imu_wz = sensors.imu.wz

    # # Do stuff with odom data.
    state.odom_x = sensors.odom.x
    state.odom_y = sensors.odom.y
    state.odom_yaw = sensors.odom.yaw

    cmd = Command()
    match state.mode:
        case 'searching':
            logger.info("I'm searching!", rate=1)

            # If we see a marker(s) note its pos and change mode.
            hexes = sensors.seen_hexes
            if len(hexes.poses) > 0:
                state.nearest_hex_id = 0
                state.nearest_hex_x = 0
                state.nearest_hex_y = 0
                nearest_hex_dist = inf

                # Check which hex is nearest to us.
                for hex_pose, hex_id in zip(hexes.poses, hexes.marker_ids):
                    dx = abs(state.odom_x - hex_pose.x)
                    dy = abs(state.odom_y - hex_pose.y)
                    if sqrt(dx**2 + dy**2) < nearest_hex_dist:
                        state.nearest_hex_x = hex_pose.x
                        state.nearest_hex_y = hex_pose.y
                        state.nearest_hex_id = hex_id
                state.mode = 'goto'
            else:
                # Drive around randomly.
                if random.random() < 0.05:
                    state.target_heading = random.uniform(-math.pi, math.pi)
                cmd.linear_vel = params.speed
                ang_error = state.target_heading - state.odom_yaw
                ang_error = math.atan2(sin(ang_error), cos(ang_error))

                logger.info(f'{ang_error}')
                cmd.angular_vel = params.p * params.turn_speed * ang_error

        case 'goto':
            logger.info('Heading towards a hex!', rate=1)
            hexes = sensors.seen_hexes

            # Try to refind the same marker each step
            if hexes is not None and hexes.poses:
                found = False
                for hex_pose, hex_id in zip(hexes.poses, hexes.marker_ids):
                    if hex_id == state.nearest_hex_id:
                        state.nearest_hex_x = hex_pose.x  # robot-frame
                        state.nearest_hex_y = hex_pose.y
                        found = True
                        break
                # If we lost sight of the marker, go back to searching
                if not found:
                    logger.info('Lost marker, returning to searching', rate=1)
                    state.mode = 'searching'
                    cmd.linear_vel = 0.0
                    cmd.angular_vel = 0.0
                    pass
            else:
                # Couldn't see any marker.
                logger.info('No markers in view, returning to searching', rate=1)
                state.mode = 'searching'
                cmd.linear_vel = 0.0
                cmd.angular_vel = 0.0
                pass

            # Continue moving towards nearest marker.
            gx, gy = state.nearest_hex_x, state.nearest_hex_y
            dist = sqrt(gx**2 + gy**2)

            # Arrival check
            if dist < 0.1:
                state.mode = 'arrived'
                bot.write(Command())  # stop
            ang = math.atan2(gy, gx)
            cmd.angular_vel = params.p * ang

            # Line robot up first.
            if abs(ang) < 1.2:
                cmd.linear_vel = params.speed
            else:
                cmd.linear_vel = 0.0

        case 'arrived':
            logger.info('Arrived at a hex!', rate=1)
            state.mode = 'searching'

    get_key(bot)
    bot.write(cmd)

    # Update our `states` matrix by inserting our `state` vector.
    states.append_row(rowdict=state.__dict__)
    logger.info(f'\nState (t={state.t_elapsed}): {state}', rate=5)


def main(log_filename='smartlog') -> None:
    """Connect to smartbot, setup plots, save data. Then loop `step()` forever.

    Switch between the real and simulated robot here. Don't forget to make sure
    the IP and smartbot_num match!
    """
    # Connect to a real robot.
    # bot = SmartBot(mode='real', drawing=True, smartbot_num=7)
    # bot.init(host='192.168.33.7', port=9090, yaml_path='default_conf.yml')

    # Connect to a sim robot.
    bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    bot.init(drawing=True, smartbot_num=3)

    # Place 8 hexes randomly inside the arena.
    for i in range(8):
        bot.engine.place_hex()

    # Create empty parameter and state objects.
    states = States()  # This gets saved to a CSV.
    params = Params()  # We can access this later in step().
    params.t0 = time()  # Record start time for this run (sec).

    # Set up plotting.
    plot_manager = setup_plotting()
    plot_manager.start_plot_proc()

    # Print out what columns exist (There may be more added later!)
    logger.info(msg=f'State Columns: {list_sensor_columns()}')

    # Run the robot!
    #######################################
    t_prev = time()
    try:
        while True:
            now = time()
            dt = now - t_prev
            t_prev = now

            bot.spin(dt)  # Get new sensor data.

            step(bot, params, states)  # <-------------- Run our code.

            # Send last row of data to plots.
            plot_manager.update_queue(data=states.iloc[-1])

            t_elapsed = time() - now
            remaining = (1 / params.controller_rate) - t_elapsed
            if remaining > 0:
                sleep(remaining)

    except KeyboardInterrupt:
        logger.info('User requesting shut down...')
    finally:
        # Save data to a CSV file.
        save_data(states, params, log_filename)
        plot_manager.stop_plot_proc()
        bot.shutdown()


if __name__ == '__main__':
    main()
