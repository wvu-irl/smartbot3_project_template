import pickle
from smartbot_irl.drawing import PlotManager


def setup_plotting() -> PlotManager:
    """Create Matplotlib figures and add line/scatter artists.

    The strings for `x_col` and `y_col` here must match column names in your
    `states` object. You can add new columns with the `state_now` dictionary in
    `step()`.

    Returns
    -------
    PlotManager

    """
    pm = PlotManager()

    # Create two windows.
    odom_fig = pm.add_figure(title='Odometry Data')
    # imu_fig = pm.add_figure(title='IMU Data')
    hex_fig = pm.add_figure(title='Hex Data')

    # Plot first hex pose.
    hex_fig.add_line(
        x_col='t_elapsed',
        y_col=['hex_x', 'hex_y', 'hex_yaw'],
        title='Hex Pose (Body Frame)',
        labels=['hex_x', 'hex_y', 'hex_yaw'],
        marker='',
        aspect='equal',
        ls='-',
        xlabel='Time (sec)',
        ylabel='Pos (m) and Angle (RAD)',
        # box_aspect=1,
    )

    # Plot odom pose data.
    odom_fig.add_line(
        x_col='t_elapsed',
        y_col=['odom_x', 'odom_y', 'odom_yaw'],
        title='2D Odom Pose',
        labels=['odomx', 'odom_y', 'odom_yaw'],
        marker='',
        aspect='equal',
        ls='-',
        xlabel='Time (sec)',
        ylabel='Pos (m) and Angle (RAD)',
        # box_aspect=1,
    )
    odom_fig.add_line(
        x_col='odom_x',
        y_col='odom_y',
        title='X-Y Position',
        marker='o',
        aspect='equal',
        xlabel='X (m)',
        ylabel='Y (m)',
    )

    # Plot all three linear accelerations (IMU)
    # for each in ['imu_ax', 'imu_ay', 'imu_az']:
    #     imu_fig.add_line(
    #         x_col='t_elapsed',
    #         y_col=[each],
    #         title=f'{each} Linear Acceleration',
    #         labels=each,
    #         marker='',
    #         # aspect="equal",
    #         window=500,
    #         xlabel='Time (sec)',
    #         ylabel='m/s^2',
    #     )
    # # Plot all three linear accelerations (IMU)
    # for each in ['imu_ax', 'imu_ay', 'imu_az']:
    #     imu_fig.add_line(
    #         x_col='t_elapsed',
    #         y_col=[each],
    #         title=f'{each} Angular Velocity',
    #         labels=each,
    #         marker='',
    #         # aspect="equal",
    #         window=500,
    #         xlabel='Time (sec)',
    #         ylabel='RAD/s',
    #     )
    return pm
