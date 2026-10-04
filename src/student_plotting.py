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

    joint_fig = pm.add_figure(title='Joint State')

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
        x_col='odom_stamp',
        y_col=['odom_x', 'odom_y', 'odom_yaw'],
        title='2D Odom Pose',
        labels=['odomx', 'odom_y', 'odom_yaw'],
        marker='',
        aspect='equal',
        ls='-',
        xlabel='Time (sec)',
        ylabel='Pos (m) and Angle (RAD)',
        window=500,
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
        window=500,
    )
    joint_fig.add_line(
        x_col='left_wheel_stamp',
        y_col='left_wheel_pos',
        title='Left joint Position',
        marker='o',
        aspect='equal',
        xlabel='X (m)',
        ylabel='Y (m)',
        window=500,
    )
    joint_fig.add_line(
        x_col='right_wheel_stamp',
        y_col='right_wheel_pos',
        title='Right joint Position',
        marker='o',
        aspect='equal',
        xlabel='X (m)',
        ylabel='Y (m)',
        window=500,
    )
    joint_fig.add_line(
        x_col='right_wheel_stamp',
        y_col='right_wheel_vel',
        title='Right joint Vel',
        marker='o',
        aspect='equal',
        xlabel='X (m)',
        ylabel='Y (m)',
        window=500,
    )
    joint_fig.add_line(
        x_col='left_wheel_stamp',
        y_col='left_wheel_vel',
        title='Left joint Vel',
        marker='o',
        aspect='equal',
        xlabel='X (m)',
        ylabel='Y (m)',
        window=500,
    )

    return pm
