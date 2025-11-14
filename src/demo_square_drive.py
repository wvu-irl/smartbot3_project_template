# demo_2dsim.py
from dataclasses import dataclass, field
import logging
# from pyclbr import Class
from time import time, sleep
import math
from math import pi
# from typing import Dict
from smartbot_irl.robot import SmartBotType
from smartbot_irl import Command, SensorData, SmartBot
from smartbot_irl.drawing import LivePlotter
from smartbot_irl.data import LaserScan, Frame, State, timestamp
from teleop import get_key_command
from smartbot_irl.utils import SmartLogger, check_realtime

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!

@dataclass
class Params:
    """ Put unchanging named values in here. Useful for "hyper parameter" kinds of values determining
    how your code will behave.
    """
    side_length: float = 2.0
    speed: float = 1.0
    turn_speed: float = 0.8
    t0: float = 0.0


def step(bot: SmartBotType, params: Params, states: State) -> None:
    """Drive a box"""
    t = time() # Current time (sec)

    # Get latest sensor data
    sensors = bot.read()
    
    # Get the last row of state data from the states dataframe.
    state_prev = states.last

    # Time driven since last state change.
    t_elapsed = t - state_prev.t_prev

    state_now = {
        "t_epoch": t,
        "time": t - params.t0,
        "t_prev": state_prev.t_prev,
        "t_elapsed": t_elapsed,
        "turning": state_prev.turning,
    }
    
    # Create an empty Command type object to be populated and then sent to the robot.
    cmd = Command()

    # Simple open-loop time based state machine.
    if not state_prev.turning:
        cmd.linear_vel = params.speed
        cmd.angular_vel = 0.0

        if t_elapsed * params.speed >= params.side_length:
            state_now["turning"] = True
            state_now["t_prev"] = t
    else:
        cmd.linear_vel = 0.0
        cmd.angular_vel = params.turn_speed

        if t_elapsed * params.turn_speed >= pi / 2:
            state_now["turning"] = False
            state_now["t_prev"] = t
    logger.info(sensors.odom)
    state_now['x'] = sensors.odom.x
    state_now['y'] = sensors.odom.y
    state_now['my_val'] = sensors.odom.yaw

    # Save the current states data vector to the states dataframe.
    states.append_row(rowdict=state_now)

    #Print out the last row of state vector data.
    logger.debug(msg=states.iloc[-1])

    # Send our commands to the robot.
    bot.write(cmd)


def main(log_file='smartlog') -> None:
    """ Set up logger, smartbot connection, plotting, and data recording. Then
    run our control loop :meth:`step` forever until stopped (e.g. <Ctrl-c>)."""

    # See more or less information (DEBUG, INFO, WARN, ERROR).
    logger.setLevel(logging.WARN)

    # Connect to a real robot.
    # bot = SmartBot(mode="real", drawing=True, smartbot_num=3)
    # bot.init(host="192.168.33.3", port=9090, yaml_path="default_conf.yml")

    # Connect to a sim robot.
    bot = SmartBot(mode="sim", drawing=True, draw_region=((-10,10),(-10,10)), smartbot_num=3)
    bot.init(drawing=True, smartbot_num=3)

    # Create empty parameter and state objects.
    states = State()
    params = Params()
    params.t0 = time()  # Start time for this run (sec)

    # Set up plotting. Create multiple figures by nesting lists in the plot_specs list.
    plot_specs = [
        [  # window 1
            ("time", "turning", "line", {"label": "Turning"}),
            ("time", "my_val",  "line", {"color": "green", "label": "Yaw"}),
            ("time", "turning", "line", {"x_window": 5.0})
        ],
        [  # window 2
            ("x", "y", "scatter", {"color": "red", "s": 3, "title": "Robot Path", "xlabel": "X", "ylabel": "Y"}),
        ],
    ]
    plotter = LivePlotter(states, plot_specs)

    # Run the robot!
    #######################################
    try:
        while True:
            t = time() # Get current time (sec).
            step(bot, params, states) # Run our code.
            check_realtime(start_t=t) # Check if our step() is taking too long.
            bot.spin() # Get new sensor data.
            plotter.update() 

    except KeyboardInterrupt:
        # Save data to a CSV file and cleanup ros+matplotlib objects.
        logger.info("Shutting down...")

        log_filename = f'{log_file}_{timestamp()}.csv'
        states.to_csv(log_filename)

        logger.info(f"Done saving to {log_filename}")
        bot.shutdown()

if __name__ == "__main__":
    main()

