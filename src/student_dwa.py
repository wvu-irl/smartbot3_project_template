import math

import numpy as np
from smartbot_irl.types import Odometry


def dynamic_window_planner(
    lidar_ranges: np.ndarray | list[float],
    lidar_angles: np.ndarray | list[float],
    odom: Odometry,
    goal_point: tuple,
    robot_radius: float = 0.16,
    max_linear_speed: float = 0.16,
    max_angular_speed: float = 0.4,
    prediction_length: float = 2.0,
    prediction_dt: float = 0.1,
    buffer: float = 0.03,
):

    # If we need to, convert the lists to numpy objects
    if type(lidar_ranges) is list[float]:
        lidar_ranges = np.array(lidar_ranges)

    if type(lidar_angles) is list[float]:
        lidar_angles = np.array(lidar_angles)

    # Remove errors
    assert isinstance(lidar_ranges, np.ndarray)
    assert isinstance(lidar_angles, np.ndarray)

    # Extract data
    curr_x = odom.x
    curr_y = odom.y
    curr_yaw = odom.yaw

    goal_x = goal_point[0]
    goal_y = goal_point[1]

    # Set up paths to try

    # Start slightly above 0 so the robot doesn't just sit there
    vels = np.linspace(0.02, max_linear_speed, 24)

    # Use an odd # for num to allow for a straight forward path
    angs = np.linspace(-max_angular_speed, max_angular_speed, 31)

    steps = int(prediction_length / prediction_dt)

    # Project the lidar data into Cartesian Space (offset is lidar position from center)
    scan_x = 0.13 + lidar_ranges * np.cos(lidar_angles)
    scan_y = lidar_ranges * np.sin(lidar_angles)

    # Remove points that are inside the robot
    valid_points = np.sqrt(scan_x**2 + scan_y**2) > robot_radius

    scan_x = scan_x[valid_points]
    scan_y = scan_y[valid_points]

    best_score = -math.inf
    lin_vel = 0
    ang_vel = 0

    for v_i in vels:
        for w_i in angs:
            # Simulate the paths
            min_dist = math.inf  # Minimum passing distance to obstacle, used in scoring
            collision = False

            # Start in the current orientation
            x_sim, y_sim, theta_sim = 0, 0, 0

            # The legs on the bus go step step step
            for t in range(steps):
                # Is there an angular component to worry about?
                if abs(w_i) > 1e-5:
                    x_sim += (v_i / w_i) * (
                        math.sin(theta_sim + w_i * prediction_dt) - math.sin(theta_sim)
                    )

                    y_sim += (v_i / w_i) * (
                        math.cos(theta_sim + w_i * prediction_dt) - math.cos(theta_sim)
                    )

                else:
                    x_sim += v_i * math.cos(theta_sim) * prediction_dt
                    y_sim += v_i * math.sin(theta_sim) * prediction_dt

                theta_sim += w_i * prediction_dt

                # Calculate distance from obstacles
                dx = scan_x - x_sim
                dy = scan_y - y_sim

                cur_min = min(np.sqrt(dx**2 + dy**2))

                # Do we go closer to objects than before?
                if cur_min < min_dist:
                    min_dist = cur_min

                    # Do we collide?
                    if min_dist < robot_radius + buffer:
                        collision = True
                        break

            # if we didn't run into anything
            if not collision:
                # Score the path
                final_world_x = curr_x + x_sim * math.cos(curr_yaw) - y_sim * math.sin(odom.yaw)
                final_world_y = curr_y + x_sim * math.sin(curr_yaw) + y_sim * math.cos(odom.yaw)

                goal_dist = np.sqrt((goal_x - final_world_x) ** 2 + (goal_y - final_world_y) ** 2)

                path_score = (
                    0.9 * min_dist  # Stay away from obstacles
                    - 0.1 * goal_dist  # Penalize large offsets from the goal
                    + 0.2 * v_i  # Go fast
                )

                if path_score > best_score:
                    best_score = path_score
                    lin_vel = v_i
                    ang_vel = -w_i

    # Did we find a viable path?
    if best_score == -math.inf:
        # Spin in a circle a bit to change views
        print('Could Not Plan Ahead, Changing View!')
        ang_vel = max_angular_speed * 0.5

    return lin_vel, ang_vel
