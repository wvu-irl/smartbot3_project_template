# SmartBot3

<br>

# Useful Commands and Keymaps

<details>
A comprehensive list of shell commands is beyond the scope of this repository. The available commands and keymaps may also vary depending on the system you are using. Fortunately there are many resources online for this, see [further reading](#further-reading) below.

- `pwd` print the **current working directory**
- `ls` list files in the **current working directory**
- `cd <path/to/file` Change Directory into the target path
- `cd ~` Move to your users HOME directory
- `rm <file>` Delete a file
- `rm -rf` Delete a directory and its files
- `clear` clear the screen

Keymaps/Shortcuts. These are pressed _simultaneously_:

- `ctrl-c` Use to kill a process (SIGINT)
- `Ctrl-Shift-c` Copy
- `Ctrl-Shift-v` Paste
- `ctrl-d`
- `ctrl-e` Move cursor to end of line
- `ctrl-a` Move cursor to beginning of line
</details>

<br>

# I am Confused and Angry About Typing Commands

<details>
`¯\_(ツ)_/¯`

## The Text Shell

A shell is any program you use to interface with a computer. A **text shell**
is, as the name implies, a text-only computer interface. Other common names are
"command prompt", "terminal", "tty". A common shell in linux is `Bash`, windows
has powershell and CMD. A **graphical shell** is how computers are most commonly
used today (buttons, windows, mouse cursor, etc).

Graphical shells are easy to learn and can be very effective. However, for the
shallow learning curve and high abstractness of a graphical shell we pay a
price. In a graphical shell if is no button or menu for what we want to do, _we
simply cannot do it_. A text shell will give you the freedom to do as you please
on your own terms provided you are willing to struggle.

Text shells are hard to learn in the same way language is hard to learn. There
is some upfront memorization necessary before you can do/say anything
non-trivial. Very quickly learning transitions away from memorization and
becomes exploration, play.

Eventually, rather than invoking the base set of commands as monosyllabic sentences
([holophrastics](https://en.wikipedia.org/wiki/Holophrasis)) you compose them.
This is not just a matter of efficiency but of being able to say entirely new
things. For example,

> "How many lines of text are there in all the python files in the current
> directory?"

becomes,

```sh
wc -l *.py
```

This is where the real power of a text interface arises. The translation of
human desire to a sequence of characters is less arcane when viewed through the
lens of sentence formation.

But just like "go", "to", and "hi" never stop being useful in human language the
base commands `cd`, `ls`, `du`, etc never stop being useful in the shell.
Fortunately the actions we need to learn how to do in the shell are relatively
few and we can quickly memorize the commands we will be repeating most often.

## The Prompt

Shells have many different forms of "prompts". A prompt is a metaphorical object where you provide your input and where additional details may be presented. Commonly the prompt will show your username along with the **current working directory** (i.e. where you are in the filesystem). This is important as the behaviour of many commands depends on _where they are run_.

```bash
username@hostname:directory$
```

Often we give **file paths** to a command and this will be affected by where the command and file path are ran.

## Copying Command Examples

Angle brackets `<>` will be used to denote an argument that is mandatory. The string inside the brackets is semantically desriptive. Do not type the brackets when actually writing the command.

```bash
cd <path/to/dir>
```

will become something like,

```bash
cd src/
```

<br>

Square brackets `[ ]` are often used to indicate optional arguments and should be interpreted the same as angle brackets otherwise.

## Further Reading:

- https://linuxjourney.com/lesson/the-shell
- [In the Beginning... Was the Command Line](https://web.stanford.edu/class/cs81n/command.txt)
- [Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html)
- https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form
- https://cheat.sh/
- https://devhints.io/bash
- https://en.wikipedia.org/wiki/Everything_is_a_file

</details>

<br>

# Installing System Dependencies

Your computer must have some minimal software packages installed before the
SmartBots can be used. Linux and windows are both supported. A mainstream Linux distro is
recommended since windows will require more troubleshooting and is generally difficult to work with.

## Linux Dependencies

<details linux_deps>
    <summary>Details</summary>
The following packages are needed:

- [Git](https://git-scm.com/install/windows)
- [Python3.12](https://www.python.org/downloads/release/python-31210/)
- [VSCode](https://code.visualstudio.com/download)

For **Debian based** distributions (Ubuntu/Mint/etc) these can be installed by
running the following command in a shell:

```bash
sudo apt update && sudo apt install git python
```

For **Arch based** distributions (Arch/PopOS/Manjaro/etc) these can be installed by
running the following command in a shell:

```bash
sudo pacman -Sy git python code
```

### Check that python was installed correctly

Check that python is installed, runnable, and the correct version by running the
following in a shell:

```bash
python --version
```

which should report `Python 3.12.10`.

</details>

## Windows Dependencies

<details win_deps>
    <summary>Details</summary>

The following packages are needed:

- [Git](https://git-scm.com/install/windows) (will install "Git" as well as "Git Bash".)
- [Python3.12 (Via Python Install Manager)](https://www.python.org/downloads/release/pymanager-250/)
- [VSCode](https://code.visualstudio.com/download)

### Git install for windows:

Download and install Git for windows.

<img src='docs/images/win_git_download.png' style="width:600;  height:auto;">

See the following gif for details if you are confused.
<img src='docs/gifs/gitbash_install.gif' style="width:800;  height:auto;">

<br>

### Python install for windows:

- Download **Python Install Manager**. This will install Python3.14 automatically
- Choose 'y' when prompted to add commands directory to your PATH
- Chose 'y' when prompted to install the CPython runtime
- Run `py install 3.12` in a shell
- Check that 1python3.121 was installed

<img src="docs/images/win_download_py_manager.png" style="max-width:600px; height:auto;">

<img src="docs/images/win_py_manager_steps.png" style="max-width:600px; height:auto;">

Then install **python3.12** using the Python Install Manager by running the following command in a command prompt shell (CMD).

```bash
py install 3.12
```

<img src="docs/images/win_py_install.png" style="max-width:600px; height:auto;">

See the following gif for details if you are confused.
<img src='docs/gifs/win_py_install.gif' style="width:800;  height:auto;">

Check that python3.12 was installed correctly by running the following in a shell:

```bash
python3.12 --version
# Python 3.12.10
```

which should report `Python 3.12.10`.

<br>

### VSCode install for windows:

Install like you would any program. If you are confused see the following gif for details.
<img src='./docs/gifs/win_vs_install.gif' style="width:800;  height:auto;">

</details>

<br>

# Setting Up Your Workspace

- Clone the repo using git
- Open the `smartbot3_project_template` folder in VSCode
- Install workspace recommended extensions
- Open a VSCode terminal (shell)
- Create a python [virtual environment](https://peps.python.org/pep-0405/) (venv)
- Install python dependencies and the python package `smartbot_irl` (included as
  a subrepo(submodule) inside the repo) into the virtual environment

## Clone the repo using git

Clone this repo with the following command (note the --recursive flag!):

```bash
git clone --recursive https://github.com/wvu-irl/smartbot3_project_template
```

This repo includes _another repo_ `smartbot_irl` which is a python package used to control the IRL SmartBot.
See the following gif for details if you are confused.
<img src='./docs/gifs/win_clone_repo.gif' style="width:800;  height:auto;">

## Open the `smartbot3_project_template` folder in VSCode

Now, let's open VSCode to the directory for the reop we have just cloned. **When prompted to install recommended extensions, click yes**. See the following gif for details if you are confused.
<img src='./docs/gifs/win_vsc_extensions_open.gif' style="width:800;  height:auto;">

## Install workspace recommended extensions

If the prompt to install recommended extensions did not appear or if you want to check for newly added recommended extensions you can search for `@recommended` in the "Extensions" menu. To download all recommended extensions click the small download button under the search bar.
<img src='./docs/images/vsc_ext_download.png' style="max-width:300;  height:auto;">

## Open a VSCode terminal (shell)

This can be done by going to the menu `View->Terminal`. Alternatively the keymap `` Ctrl-`  `` will toggle the terminal pane open/closed.

We can have VSC open a variety of shells. On windows we can select from gitbash, CMD, and powershell. You may do this by clicking on the small down arrow at the top of the terminal pane.
<img src='./docs/images/vsc_new_shell.png' style="max-width:300;  height:auto;">

We can make additional terminal windows here if desired. Alternatively, the keymap `` Ctrl-Shift-`  `` will also do this.

<img src='./docs/images/vsc_new_shell2.png' style="max-width:300;  height:auto;">

## Create a python virtual environment (venv)

> **Note**: Windows makes using python and venvs more cumbersome. Instructions
> found online will be primarily aimed at Linux and may not work for windows.

Before we can can use the `smartbot_irl` package to send and receive data from
the SmartBot we must make it importable for our python code.

We will use a python [virtual environment](https://peps.python.org/pep-0405/) in
our project so that we can more easily manage python dependencies. There are two
options for creating and manage venvs: Shell commands and VSCodes built in
tools. Both are shown here.

### Linux Venv

<details linux>

</details linux>

### Windows Venv

<details open>

### Option 1: Setting up a venv using the shell

> Make sure to run the following commands from inside the top level of the `smartbot3_project_template` you cloned!

To create a python3.12 venv in a directory named `.venv` use the command:

```bash
python3.12 -m venv .venv
```

<details >
    <summary>See the following gif for details if you are confused.</summary>
<img src='./docs/gifs/win_venv_install.gif' style="max-width:700;  height:auto;">
</details>
<br>

Then install python dependencies using `pip.exe` inside of the `.venv` directory:

```bash
.venv/Scripts/pip.exe install -r requirements.txt
```

<details>
    <summary>See the following gif for details if you are confused.</summary>
<img src='./docs/gifs/win_venv_req_install.gif' style="max-width:700;  height:auto;">
</details>
<br>

Then install the `smartbot_irl` package using:

```bash
.venv/Scripts/pip.exe install -e smartbot_irl
```

<details>
    <summary>See the following gif for details if you are confused.</summary>
<img src='./docs/gifs/win_venv_smartbot_install.gif' style="max-width:700;  height:auto;">
</details>

### Option 2: Setting up a venv using VSCode

<details vscopt>
</details vscopt>

</details win>

<br>

# Activating Robot

Before you can control the robot we must perform several steps.

- Powering On the Robot
- Start hardware interface on the robot

## Powering On the Robot

Find the big red button and rotate it CCW until it pops out ~1/4 inch and clicks. This will provide power to the motors and lidar. Power to the computer (Jetson) is provided seperately by the rocker switch. Turn this on by pushing down on the side marked with a `|`.

[Add picture](!foo)

To check if the jetson is powered, open the vanity plate (the lid) and look for a green light on the computer.

[Add picture](!foo)

## Start hardware interface on the robot

Before the robot will respond to commands the hardware interface code _on the robot_ must be running. Fortunately this has been greatly simplified. We can star the hardware interface with two methods: A VSCode task or the shell.

### Start hardware interface with VSCode task

<details open>

If the "Fast Tasks" extension was installed then several buttons will be available in the "Explorer" pane which will automate the process of starting the robot.

<img src='./docs/images/start_robot_vsc.png' style="max-width:300;  height:auto;">

<details>
    <summary>See the following gif for details if you are confused.</summary>
<img src='./docs/gifs/.gif' alt="TODO" style="max-width:700;  height:auto;">

</details>
</details>

### Start hardware interface with shell

<details vscopt>
Rather than using the VSCode task we can manually invoke the shell/powershell scripts that connect to the robot.

For linux:

```bash
bash .scripts/start_robot.bash 192.168.33.<your_robot_num> prod
```

For windows:

```bash
.scripts/start_robot_windows 192.168.33.<your_robot_num> prod
```

<details open>
    <summary>See the following gif for details if you are confused.</summary>
<img src='./docs/gifs/.gif' alt="TODO" style="max-width:700;  height:auto;">

</details>
</details vscopt>


# Running Code

> Before running code we must [activate the robot](#activating-robot)!

There are a few demo programs included in `src/`. You should add your scripts here as well. Let's try and run the teleop example. If we open it in the editor we can click the small "Play" button at the top right. If our venv is created correctly and we have installed all the dependencies a PyGame window should appear. Arrow keys will move the robot. The `PGUP/PGDOWN` keys will open/close the gripper. The keys `b/n/m` will cycle the arm through the DOWN/STOW/HOLD positions.

You may also run the script from the shell with:
```bash
python3.12 src/demo_teleop.py
```
<details>
<summary>windows</summary>

```bash
.venv/Scripts/python.exe src/demo_teleop.py
```
</details>

<details open>
    <summary>See the following gif for details if you are confused.</summary>
<img src='./docs/gifs/start_teleop.gif' alt="TODO" style="max-width:700;  height:auto;">

To cycle through shell history the UP/DOWN arrow keys can be used.

## Running in sim/real

To change between a simulated and real robot modify the "mode" string to be "real"|"sim". To choose which real robot you are connecting to specify its IP address in the `SmartBot.init()` method.

```py
    # For SmartBot2.
    bot = SmartBot(mode="real", drawing=True, smartbot_num=2)
    bot.init(host="192.168.28.254", port=9090, yaml_path="default_conf.yml")

    # For a simulated SmartBot
    # bot = SmartBot(mode="sim", drawing=True, smartbot_num=3)
    # bot.init(drawing=True, smartbot_num=3)
```

<details>
    <summary>See the following gif for details if you are confused.</summary>
<img src='docs/gifs/smartbot_real_run.gif' alt="TODO" style="max-width:700;  height:auto;">
</details>

# Using `smartbot_irl`

The main classes in the `smartbot_irl` package are `SensorData`, `Command`, and
`SmartBot`. In the example scripts we create an instance `bot` from the
`SmartBot` class. This `SmartBot` instance `bot` has the _methods(A.K.A
functions)_ `SmartBot.read()`, `SmartBot.write()`, and `SmartBot.spin()`. For
the `bot` instance of `SmartBot` you will call these functions like so:

```py
def step()
bot=SmartBot()
# The following would go in the step() function.
my_sensor_data = bot.read()
# Your algorithm here
my_command = Command(
    linear_vel = 0.3, # Move forward at 0.3m/s
    angular_vel=0.4, # Rotate CCW
    gripper_closed=True, # Close the gripper.
)
bot.write(my_command)
```

## The step() Function
This is where all your code should go. The `step()` function is called repeatedly until shutdown by the `main()` function. The `step()` function has a number of parameters passed in when it is called.

## Example Program
You can have your code mirror the following structure:

```py
```

## Sending Commands
To send commands we use `SmartBot.write()`

**Note**: We *do not* actually call `write()` like `SmartBot.write()`. Instead what this is communicating is the full name of the `write()` function which is a method of the `SmartBot` class. What this means is that we can call `write()` on any object which is of the *type* `SmartBot`. To illustrate:
```py
# `bot` is an object of type `SmartBot`.
bot = SmartBot(mode="real", drawing=True, smartbot_num=8)
# `bot` inherits the functions(methods) of its type (i.e. SmartBot).
bot.init(host="192.168.33.8", port=9090, yaml_path="default_conf.yml")
bot.write()
```

It is conceivable that you could make multiple `SmartBot` type objects to control multiple robots simultaneously. If you try this you get a gold sticker.
```py
# `bot` is an object of type `SmartBot`.
bot2 = SmartBot(mode="real", drawing=True, smartbot_num=2)
bot3 = SmartBot(mode="real", drawing=True, smartbot_num=3)
# `bot` inherits the functions(methods) of its type (i.e. SmartBot).
bot2.init(host="192.168.33.2", port=9090, yaml_path="default_conf.yml")
bot3.init(host="192.168.33.3", port=9090, yaml_path="default_conf.yml")
```

## Reading Sensor Data
To read sensor data we use `SmartBot.read()`. This is called in a similar way to `SmartBot.cmd()` but it accepts no arguments. It returns an object of type `smartbot_irl.data.SensorData`

```py
    sensors = bot.read()

```

## Using Parameters
The example scripts provides a class called `Params` where you can define parameters and their values. This is useful for values that don't change (e.g. dimensions or PID terms). This simplifies accessing parameter values so that it may be done as follows:

```py
def step(bot: SmartBotType, params: Params, states: State) -> None:
    t = time()

    state_prev = states.last # Get previous steps state vector.
    t_prev = state_prev.t_epoch # The previous steps timestamp.

    # New row vector to append to our states matrix.
    state_now = {
        "t_epoch": t,  # Seconds since Jan 1 1970.
        "t_delta": t - t_prev,  # Seconds since last time step.
        "t_elapsed": t - params.t0,  # Seconds since program start.
    }
    if state_now.t_elapsed > params.time_per_side:
        # do something
        ...
```

## Using State Data
The `States` object acts like a giant matrix. Columns are for specific variables and rows are time indices (integer count).

```py
def step(bot: SmartBotType, params: Params, states: State) -> None:
    t = time()

    state_prev = states.last # Get previous steps state vector.
    t_prev = state_prev.t_epoch # The previous steps timestamp.

    # New row vector to append to our states matrix.
    state_now = {
        "t_epoch": t,  # Seconds since Jan 1 1970.
        "t_delta": t - t_prev,  # Seconds since last time step.
        "t_elapsed": t - params.t0,  # Seconds since program start.
    }

    sensors = bot.read()

    # Let's add the sum of the IMU acceleration data as a new column.
    imu_sum = sensors.imu.ax + sensors.imu.ay + sensors.imu.az
    state_now['my_column'] = imu_sum

    # And add to the end of our state matrix.
    states.append_row(state_now)

```

## Using SmartLogger to Print
A good alternative to using `print()` is the `SmartLogger` class (which wraps pythons logging package). This allows us to rate limit print messages and to set individual message severity levels.

The logging level can be changed (DEBUG|INFO|WARN|ERROR|CRITICAL) to control the verbosity of output. This can be used so that you do not have to comment out print statements. Rather, you can leave `logger.debug(<your_msg>)` in place and instead change the log level like `logger.setLevel(logging.WARN)` in `main()` to show only WARN and above log messages.

Some example logging commands:

```py
logger.info(sensors.odom, rate=3)
logger.info(sensors.odom.x, rate=3)
logger.info(sensors.odom.y, rate=3)
logger.info(msg=state_now["joints_positions"])
logger.debug(msg=f"Number of hexes: {my_var=}", rate=1)
```

## Saving Data

## Plotting

## Autoformat

# Troubleshooting

## The dir `smartbot_irl` is empty!

Try running the following inside of your project repo

```bash
git submodule update --init --recursive
```

## Updating smartbot_irl

The directory named smartbot*irl inside of your project directory is itself a
git repo and is called a \_git submodule*. To update/reset the contents of the
smartbot_irl package you can run the following command insode of your repo:

```
git -C smartbot_irl reset --hard main
git submodule update --checkout --recursive -f
```

## I Can't Get Lidar or Move the Robot!

Check the E-Stop button is off (meaning the lidar+motors have power)! When the
E-stop is activated power is cut to the robot motors and lidar but the computer
will still receive power (if the toggle switch is on).

Another common problem is low voltage causing the lidar to stop spinning. Check if you can hear the lidar and if the battery is low.

## Updating The Template Repo

If you want to pull changes made to the template repo (not the smartbot_irl repo). Run the following in the project template directory.

```bash
git pull
```
