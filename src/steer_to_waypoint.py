# steer_to_waypoint.py, here robot steers to waypoint adjusting the linear and rotational error.
import math
from dataclasses import dataclass
from time import time

from smartbot_irl.data import State, list_sensor_columns, timestamp
from smartbot_irl.utils import SmartLogger, check_realtime, logging

from smartbot_irl import Command, SmartBot, SmartBotType
from student_plotting import setup_plotting

logger = SmartLogger(level=logging.WARN)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    linear_gain = 1
    rotational_gain = 2
    goal_x: float = -1.5
    goal_y: float = -0.5
    heading_tol: float = 0.01  # rad (~0.5 deg) -- how close is "facing the waypoint"
    distance_tol: float = 0.1  # m -- how close is "at the waypoint"


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
    sensors.imu

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

    ################################
    #     Your Code Here vvv    #
    ################################

    goal_x = params.goal_x
    goal_y = params.goal_y

    current_x = sensors.odom.x
    current_y = sensors.odom.y
    current_yaw = sensors.odom.yaw

    dx = goal_x - current_x
    dy = goal_y - current_y
    distance = math.hypot(dx, dy)
    print(f'distance to the goal is {distance}')
    desired_heading = math.atan2(dy, dx)
    error = desired_heading - current_yaw

    # Wrap heading error to [-pi, pi] so we always turn the short way.
    heading_error = math.atan2(math.sin(error), math.cos(error))
    print(f'heading error is  {heading_error}')
    lin_vel = 0.0
    ang_vel = 0.0
    if distance > params.distance_tol:
        lin_vel = params.linear_gain * distance

    if abs(heading_error) > params.heading_tol:
        ang_vel = params.rotational_gain * heading_error

    else:  # 'done'
        lin_vel = 0.0
        ang_vel = 0.0
        print('reached goal point')

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
    # bot = SmartBot(mode='real', drawing=True, smartbot_num=6)
    # bot.init(host='192.168.33.6', port=9090, yaml_path='default_conf.yml')

    # Connect to a sim robot.
    logger.info('Connecting to smartbot...')
    bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    bot.init(drawing=True, smartbot_num=3)

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
