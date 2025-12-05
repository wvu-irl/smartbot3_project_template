# demo_2dsim.py
from dataclasses import dataclass
from math import pi
from re import X
from time import sleep, time
from tkinter import Y

from smartbot_irl.data import LaserScan, State, list_sensor_columns, timestamp
from smartbot_irl.utils import SmartLogger, check_realtime, logging
from smartbot_irl import SmartBot, SmartBotType
from smartbot_irl import Command, SensorData, SmartBot
from student_plotting import setup_plotting


import numpy as np

logger = SmartLogger(level=logging.INFO)  # Print statements, but better!


@dataclass
class Params:
    max_lin_vel: float = 0.2
    max_ang_vel: float = 0.8

    t0: float = 0.0
    yaw: float = 0.0

    theta_goal: float = 0.0
    x_goal: float = 4.0
    y_goal: float = -2.0

    rad_switch: float = 0.25

    k_rho: float = 1.0
    k_alpha: float = 8.0
    k_beta: float = -2.0

    long_finish: bool = False
    rot_finish: bool = False
    short_finish: bool = False
    grasp_finish: bool = False

    P_a: float = 2.0
    I_a: float = 0.1
    D_a: float = 0.2

    P_l: float = 0.0
    I_l: float = 0.0
    D_l: float = 0.0

    lin_err_prev: float = 0.0
    ang_err_prev: float = 0.0
    ang_I_build: float = 0.0

    go: bool = False
    x_prev: float = 0.0
    y_prev: float = 0.0

    mark_x: float = 0.0
    mark_y: float = 0.0


def step(bot: SmartBotType, params: Params, states: State) -> None:
    # Get info about previous timestep state.
    state_prev = states.last
    t_prev = state_prev.t_epoch  # Last timestamp (sec).
    sensors = bot.read()
    cmd = Command()

    # Create current state vector.
    t = time()
    state_now = {
        't_epoch': t,  # Seconds since Jan 1 1970.
        't_delta': t - t_prev,  # Seconds since last time step.
        't_elapsed': t - params.t0,  # Seconds since program start.
    }

    def yaw_correction():
        sensors = bot.read()
        if sensors.odom is not None:
            if sensors.odom.yaw < 0:
                yaw = sensors.odom.yaw + 2 * pi
            else:
                yaw = sensors.odom.yaw

            return yaw
        else:
            yaw = 0.0
            return yaw

    def wrap(a):
        return (a + np.pi) % (2 * np.pi) - np.pi

    def target_comp():
        yaw = yaw_correction()
        if sensors.seen_hexes.poses is not None and len(sensors.seen_hexes.poses) > 0:
            x = sensors.seen_hexes.poses[0].x
            y = sensors.seen_hexes.poses[0].y
            c = np.sqrt(x**2 + y**2)
            if x == Params.x_prev:
                ## FAKE ##
                pass

            else:
                if y < 0.0:
                    theta = -np.acos(x / c)
                else:
                    theta = np.acos(x / c)

                phi = yaw + theta

                Params.mark_x = sensors.odom.x + c * np.cos(phi)
                Params.mark_y = sensors.odom.y + c * np.sin(phi)

                Params.x_prev = x
                Params.y_prev = y

        error_x = Params.mark_x - sensors.odom.x
        error_y = Params.mark_y - sensors.odom.y
        error_theta = Params.theta_goal - yaw

        # logger.warn(error_theta)

        return np.array([error_x, error_y, error_theta])

    def approach_long():
        # Get sensor data.

        Params.yaw = yaw_correction()
        err = target_comp()

        x_err = err[0]
        y_err = err[1]
        theta_err = err[2]

        # Update our `states` matrix by inserting our `state_now` vector.
        state_now.update(sensors.flatten())
        states.append_row(state_now)

        # logger.info(sensors.seen_hexes)

        rho = np.sqrt(x_err**2 + y_err**2)
        # logger.warn(rho)
        alpha = wrap(np.atan2(y_err, x_err) - Params.yaw)
        beta = wrap(theta_err - alpha - Params.yaw)

        ###################################################################
        ### Control Law ###################################################
        ###################################################################

        v = Params.k_rho * rho
        w = Params.k_alpha * alpha + Params.k_beta * beta

        if rho <= 0.2:
            cmd.angular_vel = 0.0
            cmd.linear_vel = 0.0
            Params.long_finish = True
        else:
            if v > Params.max_lin_vel:
                cmd.linear_vel = Params.max_lin_vel
            else:
                cmd.linear_vel = Params.max_ang_vel * v

            # logger.warn(w)
            if w > Params.max_ang_vel:
                cmd.angular_vel = Params.max_ang_vel
            else:
                cmd.angular_vel = Params.max_ang_vel * w
                # print('Still Turning!!!')

    def rotate_goal():
        err = target_comp()
        theta_err = err[2] - np.pi
        logger.warn(theta_err)

        yaw = yaw_correction()

        if abs(theta_err - yaw) <= 0.05:
            cmd.linear_vel = 0.0
            cmd.angular_vel = 0.0
            Params.rot_finish = True
        else:
            p_gain = (theta_err - yaw) * Params.max_ang_vel

            if abs(p_gain) >= Params.max_ang_vel:
                cmd.linear_vel = 0.0
                if p_gain <= 0.0:
                    cmd.angular_vel = -Params.max_ang_vel
                else:
                    cmd.angular_vel = Params.max_ang_vel
            else:
                cmd.linear_vel = 0.0
                cmd.angular_vel = p_gain

    def approach_short():
        Params.yaw = yaw_correction()
        err = target_comp()
        x_err = err[0]
        y_err = err[1]
        theta_err = err[2] - np.pi

        def ang_PID():
            ang_err = theta_err - Params.yaw
            d_ang_err = (ang_err - Params.ang_err_prev) / state_now['t_delta']
            i_ang_err = Params.ang_I_build + (ang_err * state_now['t_delta'])

            P = Params.P_a * ang_err
            I = Params.I_a * i_ang_err
            D = Params.D_a * d_ang_err
            PID_a = P + I + D

            a = min(PID_a, Params.max_ang_vel)
            cmd.angular_vel = a

            # will probably have to change this to focus on y instead of theta
            # maybe have to look at both just to ensure alignment

        def lin_PID():
            mark_x = Params.x_goal + np.random.normal(0, 0.02) - sensors.odom.x
            mark_y = Params.y_goal + np.random.normal(0, 0.02) - sensors.odom.y
            lin_err = np.sqrt(mark_x**2 + mark_y**2)
            logger.warn(lin_err)
            if lin_err <= 0.1:
                cmd.linear_vel = 0.0
            else:
                v = min(lin_err, Params.max_lin_vel)
                cmd.linear_vel = -v

        #### PID Loop to drive backwards towards marker ####
        ang_PID()
        lin_PID()

    if sensors.seen_hexes.poses is not None and len(sensors.seen_hexes.poses) > 0:
        Params.go = True

    if Params.go == True:
        approach_long()

    bot.write(cmd)


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
            plot_manager.update_all(states.iloc[-1])

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
