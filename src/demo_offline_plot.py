import pandas as pd
import matplotlib.pyplot as plt

# Which CSV to load.
csv_path = "smartlog_2025-11-13_13-53-01.csv"
######################################################

df = pd.read_csv(csv_path)
print(df.columns)

# Grab a specific range of data
t_start, t_end = 1.2, 3.5
sub_df = df[(df["t_elapsed"] >= t_start) & (df["t_elapsed"] <= t_end)]


# -----------------------------
# Window 1: time vs odom_x
# -----------------------------
fig1, ax1 = plt.subplots()
ax1.plot(sub_df["t_elapsed"], sub_df["odom_x"])
ax1.set_xlabel("t_elapsed")
ax1.set_ylabel("odom_x")
ax1.set_title("odom_x vs time")

# -----------------------------
# Window 2: XY path
# -----------------------------
fig2, ax2 = plt.subplots()
ax2.scatter(sub_df["odom_x"], y=sub_df["odom_y"], s=5, color="red")
ax2.set_aspect("equal", adjustable="box")
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_title("Robot Path")

# Show all figures
plt.show()
