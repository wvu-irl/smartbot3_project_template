# SmartBot3 Mobile Robotics

# System Dependencies

On your computer you must have the following installed.

* [Git](https://git-scm.com/install/windows)
* [Python3.12](https://www.python.org/downloads/release/python-31210/)
* [VSCode](https://code.visualstudio.com/download)

"Git for Windows" will install the version control software "Git" as well as "Git Bash".

After installing python3.12 check your python version by running the following in a gitbash shell:
```bash
$ python --version
```

which should report `Python 3.12.10`.

# Setting Up Your Workspace
* Clone repo
* `cd` into cloned repo directory
* Open repo folder in VSCode 
* Create a python virtual environment (venv)
* Pip install `smartbot_irl` and python deps into the virtual environment

Open the program [**Git Bash**](https://www.atlassian.com/git/tutorials/git-bash) which was installed with Git. This is minimal bash-like text shell where we will type commands. Run the following to download the template repo:

```bash
git clone --recursive <repo_url>
cd <dir_name>
ls -a
```
![clone_and_ls](docs/clone_and_ls.gif)


This repo includes the `smartbot_irl` python package which we will use to control the IRL SmartBot. We will use a python **virtual environment** in our repos so that we can more easily install python packages. To create a virtual environment directory named `.venv` we will use VSCodes built in python tools.

Open VSCode and select **"Open Folder"** on the cloned repo. Install any recommended extensions. Then open the **command palette** with the keymap `<Ctrl-Shift-p>` and type `environment`. Select `Python: Create Environment` -> `Venv`. Wait for the packages in `requirements.txt to be installed to our venv.
![clone_and_ls](docs/open_pip_requirements.gif)


Now we will install the `smartbot_irl` package to our venv as well so we can use it in our code. To do this open a terminal (check that the venv is active by looking for text like `(venv)` ) in vscode and run the following **inside the repo**.
```
pip install -e smartbot_irl
```
This will make an editable install of the `smartbot_irl` to your venv. To see if the venv is active look for text like `(venv)` in your terminal. If it is not active them your python code will not be able to find the packages we have installed
![clone_and_ls](docs/smartbot_install.gif)

<!-- ```bash
python3 -m venv .venv # Run this inside the repo
```
which should result in a new directory named `<your_repo>/.venv` which is a **hidden directory** that can be seen with the command `ls -a`. 

Now to install `smartbot_irl` and dependencies **from inside the repo** run:
```bash
.venv/Scripts/pip install -e smartbot_irl
```

[More information on VSCode and venv's](https://code.visualstudio.com/docs/python/python-tutorial#_start-vs-code-in-a-workspace-folder)

![venv_and_pip](docs/venv_and_pip.gif) -->

# Running Code
There are a few demo programs included in `src/`. You should add your scripts here as well. Let's try and run the teleop example. If we open it in the editor we can click the small "Play" button at the top right. If our venv is created correctly and we have installed all the dependencies a PyGame window should appear. Arrow keys will move the robot. The PGUP/PGDOWN keys will open/close the gripper. The keys b/n/m will cycle the arm through the DOWN/STOW/HOLD positions.

You may also run the script from the gitbash shell with
```bash
.venv/Scripts/python.exe c:/Users/n/test_mobile_robotics_template/src/demo_teleop.py
```
![clone_and_ls](docs/start_teleop.gif)


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
![clone_and_ls](docs/smartbot_real_run.gif)
