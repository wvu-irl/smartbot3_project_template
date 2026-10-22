# gyro_integration.py
"""Estimate robot Euler angles (roll, pitch, yaw) by integrating rate-gyro data.

Steps:
1. For the first `bias_duration` seconds the robot is held still and gyro
   readings are collected (skipping the first `settle_time` seconds while the
   IMU starts streaming). Their median is used as the gyro bias.
2. After that, bias-corrected rates (p, q, r) are integrated with the
   discretized Euler-angle kinematics, using the measured time step T_s:

    phi_k   = phi_{k-1}   + T_s (p + q sin(phi) tan(theta) + r cos(phi) tan(theta))
    theta_k = theta_{k-1} + T_s (q cos(phi) - r sin(phi))
    psi_k   = psi_{k-1}   + T_s (q sin(phi) / cos(theta) + r cos(phi) / cos(theta))

   where all right-hand side terms are taken from step k-1.
3. The user can tele-operate the robot with the arrow keys the whole time.
"""

import math
from dataclasses import dataclass, field
from time import time

import numpy as np
from smartbot_irl.data import State, list_sensor_columns, timestamp
from smartbot_irl.drawing import PlotManager
from smartbot_irl.utils import SmartLogger, check_realtime, logging

from smartbot_irl import Command, SmartBot, SmartBotType
from student_teleop import get_key_command

logger = SmartLogger(level=logging.WARN)  # Print statements, but better!


@dataclass
class Params:
    """Put static values in here (e.g. PID values)."""

    t0: float = 0.0

    # Bias removal.
    bias_removal: bool = True  # False = skip calibration and integrate raw gyro data.
    bias_duration: float = 15.0  # Seconds to keep still and collect gyro samples.
    settle_time: float = 1.0  # Seconds of samples to skip while the IMU starts up.
    bias_samples: list = field(default_factory=list)  # Raw (wx, wy, wz) samples.
    bias: tuple = (0.0, 0.0, 0.0)  # Median gyro bias (p, q, r).
    calibrated: bool = False

    # Integration state (step k-1). Initial Euler angles are zeros.
    phi: float = 0.0  # Roll (rad).
    theta: float = 0.0  # Pitch (rad).
    psi: float = 0.0  # Yaw (rad).
    p_prev: float = 0.0  # Bias-corrected body rates from step k-1 (rad/s).
    q_prev: float = 0.0
    r_prev: float = 0.0
    t_prev: float = 0.0  # Timestamp of step k-1 (sec).


def integrate_gyro(params: Params, t: float, p: float, q: float, r: float) -> None:
    """Advance the Euler angle estimate by one time step (forward Euler)."""

    #  time stamp
    Ts = t - params.t_prev

    # Values from the previous step (k-1).
    phi, theta, psi = params.phi, params.theta, params.psi
    pk, qk, rk = params.p_prev, params.q_prev, params.r_prev

    # Avoid dividing by zero at the pitch = +/-90 deg singularity.
    cos_theta = math.cos(theta)
    if abs(cos_theta) < 1e-6:
        cos_theta = math.copysign(1e-6, cos_theta)

    phi_dot = pk + qk * math.sin(phi) * math.tan(theta) + rk * math.cos(phi) * math.tan(theta)
    theta_dot = qk * math.cos(phi) - rk * math.sin(phi)
    psi_dot = qk * math.sin(phi) / cos_theta + rk * math.cos(phi) / cos_theta

    params.phi = phi + Ts * phi_dot
    params.theta = theta + Ts * theta_dot
    params.psi = psi + Ts * psi_dot

    # Save current values to be used as (k-1) in the next step.
    params.p_prev, params.q_prev, params.r_prev = p, q, r
    params.t_prev = t


def step(bot: SmartBotType, params: Params, states: State) -> None:
    """This is the main control loop for the robot. Code here should run in <50ms."""

    # Create current state vector.
    t = time()
    state_prev = states.last
    state_now = {
        't_epoch': t,  # Seconds since Jan 1 1970.
        't_delta': t - state_prev.t_epoch,  # Seconds since last time step.
        't_elapsed': t - params.t0,  # Seconds since program start.
    }

    # Get sensor data. Gyro rates about body x, y, z = (p, q, r).
    sensors = bot.read()
    wx, wy, wz = sensors.imu.wx, sensors.imu.wy, sensors.imu.wz
    logger.warn(f'{sensors.joints.left_vel}')
    # Read the keyboard every step (also lets the user quit with 'q').
    cmd = get_key_command(sensors)

    if params.bias_removal and not params.calibrated:
        # Bias removal: keep the robot still and collect gyro samples.
        cmd = Command()
        # Skip the start-up period and any all-zero readings (IMU not streaming yet).
        imu_ready = (wx, wy, wz) != (0.0, 0.0, 0.0)
        if state_now['t_elapsed'] >= params.settle_time and imu_ready:
            params.bias_samples.append((wx, wy, wz))

        if state_now['t_elapsed'] >= params.bias_duration and params.bias_samples:
            params.bias = tuple(np.median(np.array(params.bias_samples), axis=0))
            params.calibrated = True
            params.t_prev = t  # Start integration from now.
            print(
                f'Bias removed: p={params.bias[0]:.4f}, q={params.bias[1]:.4f}, r={params.bias[2]:.4f}'
            )
            print('Calibration done. Ready to move! Use the arrow keys to drive.')
    else:
        # Remove bias, then integrate.
        p = wx - params.bias[0]
        q = wy - params.bias[1]
        r = wz - params.bias[2]
        integrate_gyro(params, t, p, q, r)

    bot.write(cmd)

    # Add new columns to our state vector.
    state_now['imu_wx'] = wx
    state_now['imu_wy'] = wy
    state_now['imu_wz'] = wz
    state_now['roll'] = params.phi
    state_now['pitch'] = params.theta
    state_now['yaw'] = params.psi
    state_now['yaw_wrapped'] = math.atan2(math.sin(params.psi), math.cos(params.psi))

    # Update our `states` matrix by inserting our `state_now` vector.
    states.append_row(rowdict=state_now)
    logger.info(f'\nState (t={state_now["t_elapsed"]:.2f}): {state_now}')


def setup_plotting() -> PlotManager:
    """Plot the gyro rates and the estimated Euler angles."""
    pm = PlotManager()
    fig = pm.create_figure(title='Gyro Integration')

    fig.add_line(
        x_col='t_elapsed',
        y_col=['imu_wx', 'imu_wy', 'imu_wz'],
        title='Gyro Rates',
        labels=['p (wx)', 'q (wy)', 'r (wz)'],
        marker='',
        ls='-',
        xlabel='Time (sec)',
        ylabel='Rate (rad/s)',
        window=500,
    )
    fig.add_line(
        x_col='t_elapsed',
        y_col=['roll', 'pitch', 'yaw_wrapped'],
        title='Euler Angles',
        labels=['roll', 'pitch', 'yaw'],
        marker='',
        ls='-',
        xlabel='Time (sec)',
        ylabel='Angle (rad)',
        window=500,
    )
    return pm


def main(log_file='gyro_log') -> None:
    """Connect to smartbot, setup plots, save data. Then loop `step()` forever.

    Switch between the real and simulated robot here. Don't forget to make sure
    the IP and smartbot_num match!

    Parameters
    ----------
    log_file : str, optional
        Filename to save data as a CSV, by default 'gyro_log'
    """

    # Connect to a real robot.
    # bot = SmartBot(mode='real', drawing=True, smartbot_num=6)
    # bot.init(host='192.168.33.6', port=9090, yaml_path='default_conf.yml')

    # Connect to a sim robot.
    # logger.info('Connecting to smartbot...')
    bot = SmartBot(mode='sim', drawing=True, draw_region=((-10, 10), (-10, 10)), smartbot_num=3)
    bot.init(drawing=True, smartbot_num=3)

    # Create empty parameter and state objects.
    states = State()  # This gets saved to a CSV.
    params = Params()  # We can access this later in step().
    params.t0 = time()  # Record start time for this run (sec).

    bot.write(Command(reset_position=True))
    params.t_prev = params.t0  # Integration starts now (used when bias_removal is False).
    if params.bias_removal:
        print(
            f'Waiting for IMU data, then calibrating for {params.bias_duration:.0f} s. Keep the robot still!'
        )
    else:
        print('Bias removal OFF. Ready to move! Use the arrow keys to drive.')

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
        print('Stopping robot...')
    finally:
        # Save data to a CSV file and cleanup ros+matplotlib objects.
        log_filename = f'{log_file}_{timestamp()}.csv'
        states.to_csv(log_filename)
        print(f'Data saved to {log_filename}')
        plot_manager.stop_plot_proc()

        bot.shutdown()


if __name__ == '__main__':
    main()
