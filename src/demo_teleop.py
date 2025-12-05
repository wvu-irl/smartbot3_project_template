# demo_2dsim.py
from dataclasses import dataclass
from time import time

from smartbot_irl import SmartBot, SmartBotType
from smartbot_irl.data import State, list_sensor_columns, timestamp
from smartbot_irl.utils import SmartLogger, check_realtime, logging

from student_plotting import setup_plotting
from student_teleop import get_key_command

logger = SmartLogger(level=logging.WARN)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    side_length: float = 2.0
    speed: float = 1.0
    turn_speed: float = 0.8
    t0: float = 0.0


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

    # Get a Command obj using teleop.
    cmd = get_key_command(sensors)
    bot.write(cmd)

    # Update our `states` matrix by inserting our `state_now` vector.
    # state_now.update(sensors.flatten())
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

    # Connect to a real robot.
    # bot = SmartBot(mode='real', drawing=True, smartbot_num=7)
    # bot.init(host='192.168.33.7', port=9090, yaml_path='default_conf.yml')

    # Connect to a sim robot.
    logger.info('Connecting to smartbot...')
    bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    bot.init(drawing=True, smartbot_num=3)

    # Create empty parameter and state objects.
    states = State()  # This gets saved to a CSV.
    params = Params()  # We can access this later in step().
    params.t0 = time()  # Record start time for this run (sec).

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
        logger.info(f'Done saving to {log_filename}')
        plot_manager.stop_plot_proc()

        bot.shutdown()


if __name__ == '__main__':
    main()
