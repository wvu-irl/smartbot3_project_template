from smartbot_irl.drawing._plotting import PlotManager


def setup_plotting() -> PlotManager:
    """Create Matplotlib figures and add line/scatter artists.

    Returns
    -------
    PlotManager

    """
    pm = PlotManager()

    # Create two windows.
    odom_fig = pm.add_figure(title='Odometry Data')
    imu_fig = pm.add_figure(title='IMU Data')

    # Add line/scatter plots using columns of the `states` object.
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
    odom_fig.add_scatter(
        x_col='odom_x',
        y_col='odom_y',
        title='X-Y Position',
        marker='o',
        aspect='equal',
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
    return pm
