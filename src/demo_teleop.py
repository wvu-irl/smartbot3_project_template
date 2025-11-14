# demo_2dsim.py
import logging
import math
from math import pi
from smartbot_irl.robot import SmartBotType
from smartbot_irl import Command, SensorData, SmartBot
from smartbot_irl.data import LaserScan, list_sensor_columns
from teleop import get_key_command
from dataclasses import dataclass, field
from time import time, sleep
from smartbot_irl.drawing import LivePlotter, PlotManager, FigureWrapper
from smartbot_irl.data import LaserScan, Frame, State, timestamp
from smartbot_irl.utils import SmartLogger, check_realtime
import matplotlib.pyplot as plt

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
    logger.debug(msg=f"{forward_range=}", rate=1)
    return forward_range


def step(bot: SmartBotType, params: Params, states: State) -> None:
    """This is the main control loop for the robot. Code here should run in <50ms."""
    t = time()

    # Get previous steps state vector.
    state_prev = states.last

    # The previous steps timestamp.
    t_prev = state_prev.t_epoch

    # New row vector to append to our states matrix.
    state_now = {
        "t_epoch": t,  # Seconds since Jan 1 1970.
        "t_delta": t - t_prev,  # Seconds since last time step.
        "t_elapsed": t - params.t0,  # Seconds since program start.
    }

    # Get sensor data.
    sensors = bot.read()

    # Get range directly ahead.
    range_forward = get_range_forward(sensors.scan)
    # logger.info(msg=f"{range_forward=}", rate=1)

    # Add a new state column named 'range_forward' if it does not already exist
    # and and insert a value.
    state_now.update({"range_forward": range_forward})

    ax = sensors.imu.ax
    ay = sensors.imu.ay
    wz = sensors.imu.wz

    ax = sensors.imu.ax
    state_now["ax"] = ax
    logger.debug(sensors.imu)

    cmd = get_key_command(sensors)
    bot.write(cmd)

    # Insert our state vector and *all* sensor data for the current timestep into the state matrix.
    state_now.update(sensors.flatten())
    states.append_row(state_now)
    # logger.info(msg=state_now['imu_linear_acceleration_x'])


def main(log_file="smartlog") -> None:
    """Set up logger, smartbot connection, plotting, and data recording. Then
    run our control loop :meth:`step` forever until stopped (e.g. <Ctrl-c>)."""

    # See more or less information (DEBUG, INFO, WARN, ERROR).
    logger.setLevel(logging.INFO)

    # Connect to a real robot.
    # bot = SmartBot(mode="real", drawing=True, smartbot_num=3)
    # bot.init(host="192.168.33.3", port=9090, yaml_path="default_conf.yml")

    # Connect to a sim robot.
    bot = SmartBot(mode="sim", drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    bot.init(drawing=True, smartbot_num=3)

    # Create empty parameter and state objects.
    states = State()
    params = Params()
    params.t0 = time()  # Start time for this run (sec)

    # Set up plotting. (<var1>, <var2>, <line|scatter|>, {"option": val})
    # plot_specs = [
    #     [  # window 1
    #         (
    #             "t_elapsed",
    #             "imu_ax",
    #             "line",
    #             {
    #                 "title": "IMU X linear accel",
    #                 "xlabel": "Time(sec)",
    #                 "ylabel": r"$\text{m / s}^2$",
    #                 "x_window": 5.0,
    #             },
    #         ),
    #         (
    #             "t_elapsed",
    #             "imu_ay",
    #             "line",
    #             {
    #                 "title": "IMU Y linear accel",
    #                 "xlabel": "Time(sec)",
    #                 "ylabel": r"$\text{m / s}^2$",
    #                 "x_window": 5.0,
    #             },
    #         ),
    #         # (
    #         #     "t_elapsed",
    #         #     "imu_ax",
    #         #     "line",
    #         #     {
    #         #         "title": "IMU X linear Accel",
    #         #         "xlabel": "Time(sec)",
    #         #         "ylabel": r"$\text{RAD / s}$",
    #         #         "x_window": 5.0,
    #         #     },
    #         # ),
    #     ],
    #     [  # window 2
    #         (
    #             "odom_x",
    #             "odom_y",
    #             "scatter",
    #             {
    #                 "color": "red",
    #                 "s": 3,
    #                 "title": "Robot Path",
    #                 "xlabel": "X",
    #                 "ylabel": "Y",
    #                 "equal_aspect": True,
    #             },
    #         ),
    #     ],
    # ]
    # plotter = LivePlotter(states, plot_specs)
    pm = PlotManager()
    odom_fig = pm.add_figure(title="Odometry Data")
    imu_fig = pm.add_figure(title="IMU Data")

    odom_fig.add_line(
        x_col="t_elapsed",
        y_col="odom_x",
        title="X Position",
        labels="odomx",
        marker="",
        ls="-",
        xlabel="Time (sec)",
        ylabel="Pos (m)",
        box_aspect=1,
    )
    odom_fig.add_scatter(
        x_col="odom_x",
        y_col="odom_y",
        title="X-Y Position",
        marker="o",
        aspect="equal",
        xlabel="X (m)",
        ylabel="Y (m)",
    )

    imu_fig.add_line(
        x_col="t_elapsed",
        y_col=["imu_ax", "imu_ay", "imu_az"],
        title="Linear Acceleration",
        labels=["Ax", "Ay", "Az"],
        marker="",
        # aspect="equal",
        xlabel="Time (sec)",
        ylabel="m/s^2",
    )

    imu_fig.add_line(
        x_col="t_elapsed",
        y_col=["imu_wx", "imu_wx", "imu_wz"],
        title="Angular Velocity",
        marker="",
        # aspect="equal",
        xlabel="Time (sec)",
        ylabel="RAD/s",
    )

    plt.show(block=False)

    logger.info(f"State Columns: {list_sensor_columns()}")

    # Run the robot!
    #######################################
    try:
        while True:
            t = time()  # Get current time (sec).
            step(bot, params, states)  # Run our code.
            check_realtime(start_t=t)  # Check if our step() is taking too long.
            bot.spin()  # Get new sensor data.
            # Send last row of data to plotter.
            pm.update_all(states.iloc[-1])

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        # Save data to a CSV file and cleanup ros+matplotlib objects.
        logger.info("Shutting down...")

        log_filename = f"{log_file}_{timestamp()}.csv"
        states.to_csv(log_filename)

        logger.info(f"Done saving to {log_filename}")
        bot.shutdown()


if __name__ == "__main__":
    main()
