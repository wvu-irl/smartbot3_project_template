# demo_2dsim.py
from dataclasses import dataclass
from math import pi
from time import sleep, time
from typing import Optional

from smartbot_irl import sim2d, SmartBot, SmartBotType
from smartbot_irl.data import LaserScan, States, list_sensor_columns, timestamp
from smartbot_irl.utils import SmartLogger, check_realtime, logging, get_log_dir, save_data

from student_plotting import setup_plotting
from student_teleop import get_key

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    side_length: float = 2.0
    speed: float = 1.0
    turn_speed: float = 0.8
    t0: float = 0.0
    controller_rate: float = 50.0
    log_filename: Optional[str] = None


def step(bot: SmartBotType, params: Params, states: States) -> None:
    """This is the main control loop for the robot. Code here should run in <50ms."""

    # Get info about previous timestep state.
    state_prev = states.last
    t_prev = state_prev.t_epoch  # Last timestamp (sec).

    # Create current state vector.
    t = time()
    state_now = {
        't_epoch': t,  # Seconds since Jan 1, 1970.
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

    for each in sensors.seen_hexes.poses:
        print(each)

    # Get a Command obj using teleop.
    cmd = get_key(bot)
    bot.write(cmd)

    # Update our `states` matrix by inserting our `state_now` vector.
    states.append_row(state_now)
    # logger.info(f'\nState (t={state_now["t_elapsed"]}): {state_now}')


def main(log_filename='smartlog') -> None:
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
            plot_manager.update_queue(states.iloc[-1])

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
