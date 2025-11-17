# demo_2dsim.py
from dataclasses import dataclass
from math import pi
from time import sleep, time

from smartbot_irl.data import LaserScan, State, list_sensor_columns, timestamp
from smartbot_irl.drawing import PlotManager
from smartbot_irl.utils import SmartLogger, check_realtime, logging

from smartbot_irl import SmartBot, SmartBotType
from teleop import get_key_command

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    side_length: float = 2.0
    speed: float = 1.0
    turn_speed: float = 0.8
    t0: float = 0.0


def get_range_forward(scan: LaserScan) -> float:
    """
    Find range directly forward. Scan starts at -2piRAD -> ranges[0].

    forward_range = (0RAD - 2piRAD) / angle_per_incremenFor coordinate
    conventions see REP 103 and REP 105:
    https://www.ros.org/reps/rep-0105.html
    https://www.ros.org/reps/rep-0103.html
    )
    """
    forward_index = int((0 * pi - scan.angle_min) / scan.angle_increment)
    forward_range = scan.ranges[forward_index]
    logger.debug(msg=f'{forward_range=}', rate=1)
    return forward_range


def setup_plotting() -> PlotManager:
    """ """
    pm = PlotManager()

    odom_fig = pm.add_figure(title='Odometry Data')
    imu_fig = pm.add_figure(title='IMU Data')
    joint_fig = pm.add_figure(title='Joints')

    # Add line/scatter plots using columns of the `states` object.
    odom_fig.add_line(
        x_col='t_elapsed',
        y_col=['odom_x', 'odom_y', 'odom_z'],
        title='X Position',
        labels='odomx',
        marker='',
        aspect='equal',
        ls='-',
        xlabel='Time (sec)',
        ylabel='Pos (m)',
        # box_aspect=1,
    )
    odom_fig.add_scatter(
        x_col='odom_x',
        y_col='odom_y',
        title='X-Y Position',
        marker='o',
        aspect='equal',
        xlabel='X (m)',
        ylabel='Y (m)',
    )
    # Roll, pitch, yaw
    odom_fig.add_line(
        x_col='t_elapsed',
        y_col=['odom_roll', 'odom_pitch', 'odom_yaw'],
        title='Odom: Roll, Pitch, Yaw',
        labels=['odom_roll', 'odom_pitch', 'odom_yaw'],
        marker='o',
        # aspect="equal",
        xlabel='X (m)',
        ylabel='Y (m)',
    )

    imu_fig.add_line(
        x_col='t_elapsed',
        y_col=['imu_ax', 'imu_ay', 'imu_az'],
        title='Linear Acceleration',
        labels=['Ax', 'Ay', 'Az'],
        marker='',
        # aspect="equal",
        window=10,
        xlabel='Time (sec)',
        ylabel='m/s^2',
    )

    imu_fig.add_line(
        x_col='t_elapsed',
        y_col=['imu_wx', 'imu_wx', 'imu_wz'],
        title='Angular Velocity',
        marker='',
        # aspect="equal",
        xlabel='Time (sec)',
        window=100,
        ylabel='RAD/s',
    )
    # joint_fig.add_line(
    #     x_col="t_elapsed",
    #     y_col=["range_forward"],
    #     title="Range Forward",
    #     # labels=["Positions", "Velocities"],
    #     marker="",
    #     # aspect="equal",
    #     xlabel="Time (sec)",
    #     ylabel="m",
    # )
    joint_fig.add_line(
        x_col='t_elapsed',
        y_col=['joints_positions'],
        title='Joints',
        # labels=["Positions", "Velocities"],
        marker='',
        # aspect="equal",
        xlabel='Time (sec)',
        ylabel='RAD/s',
    )

    return pm


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

    # Get range directly ahead.
    # range_forward = get_range_forward(sensors.scan)
    # logger.info(msg=f'{range_forward=}', rate=1)

    # # Add column named `range_forward` if it does not already exist
    # state_now['range_forward'] = range_forward

    # Do stuff with IMU data.
    logger.debug(sensors.imu)
    ax = sensors.imu.ax
    ay = sensors.imu.ay
    wz = sensors.imu.wz
    state_now['ax'] = ax
    state_now['ay'] = ay
    state_now['wz'] = wz

    # Drive robot using a keyboard.
    cmd = get_key_command(sensors)
    bot.write(cmd)

    # Update our `states` matrix by inserting our `state_now` vector.
    state_now.update(sensors.flatten())
    states.append_row(state_now)

    logger.info(sensors.seen_hexes)


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
    bot = SmartBot(mode='real', drawing=True, smartbot_num=7)
    bot.init(host='192.168.33.7', port=9090, yaml_path='default_conf.yml')

    # Connect to a sim robot.
    # bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    # bot.init(drawing=True, smartbot_num=3)

    # Create empty parameter and state objects.
    states = State()  # This gets saved to a CSV.
    params = Params()  # We can access this later in step().
    params.t0 = time()  # Record start time for this run (sec).

    # Set up plotting.
    plot_manager = setup_plotting()
    plot_manager.show_plots()

    # Print out what columns exist (There may be more later!)
    logger.info(msg=f'State Columns: {list_sensor_columns()}')

    # Run the robot!
    #######################################
    try:
        while True:
            step(bot, params, states)  # Run our code.
            check_realtime(start_t=time())  # Check if our step() is taking too long.
            bot.spin()  # Get new sensor data.

            # Send last row of data to plots.
            plot_manager.update_all(states.iloc[-1])
            # sleep(0.001)

    except KeyboardInterrupt:
        logger.info('User requesting shut down...')
    finally:
        # Save data to a CSV file and cleanup ros+matplotlib objects.
        log_filename = f'{log_file}_{timestamp()}.csv'
        states.to_csv(log_filename)
        logger.info(f'Done saving to {log_filename}')

        bot.shutdown()


if __name__ == '__main__':
    main()
