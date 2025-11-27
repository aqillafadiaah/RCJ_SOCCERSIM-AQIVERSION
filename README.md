# RCJ Soccer Simulator

This is the official repository of the RoboCupJunior Soccer Simulator. The
simulator is based on [Webots](https://github.com/cyberbotics/webots) and this
repository provides both the "automatic referee" (which implements the [Soccer
Simulated Rules](https://github.com/robocup-junior/soccer-rules-simulation))
as well as a sample simulated team of robots with some basic strategy.

*Learn more in the [documentation](https://robocup-junior.github.io/rcj-soccersim/).*

# How do I try this out?

## Installation

1. The first thing you need to prepare is installing Python. Go to https://www.python.org/downloads/ and download the latest version for your system.

2. Next, download the Soccer Simulator. You can get it from https://github.com/robocup-junior/rcj-soccersim.git or from the revised version provided to you. After opening the page, click the Code button and select Download ZIP.

3. If you prefer not to extract a ZIP file, you can download the project directly through the terminal or command prompt using the following command. Wait a moment until all files finish downloading.

4. If you downloaded the ZIP file from the website, extract it.

5. Before opening Webots, make sure you have all the required files prepared properly.

6. The next step is optional, but recommended if you plan to edit the code or contribute to this repository. This keeps the project organized. Open the terminal or command prompt and run the command shown below.
   Langkah 1
   cd rcj-soccersim
   
   Langkah 2
   python3 -m venv venv
   
   Langkah 3
   source venv/bin/activate
   
   Langkah 4
   pip install pip-tools atau pip3 install pip-tools
   
   Langkah 5
   pip-sync requirements/development.txt
   
   Langkah 6
pre-commit install

7. After that, open Webots. Go to File > Open World, navigate to the worlds folder, and select soccer.wbt.

8. Once loaded, you’ll see the soccer field, six differential-drive robots (two teams with three robots each), both goals, and the arena boundaries.

9. Set the starting formation for your match strategy. In this example, we use a 2–1 formation: B1 and Y1 as strikers, B2 and Y2 as midfielders, and B3 and Y3 as goalkeepers.

10. Open the Scene Tree panel on the left. This panel contains all robot and arena configurations. Adjust the translation and rotation of each robot to position them according to the 2–1 formation. Leave the ball unchanged.
    Robot Configuration
 
    Robot; translasi (x), (y), (z) ; rotasi (x), (y), (z), (angle)
    B1   ; translasi (0.25), (0.25), (0.042) ; rotasi (0), (0), (-1), (1.57)
    B2   ; translasi (-0.25), (0.25), (0.042) ; rotasi (0), (0), (-1), (1.57)
    B3   ; translasi (0), (0.75), (0.042) ; rotasi (0), (0), (1), (0)
    
    Y1   ; translasi (-0.25), (-0.25), (0.042) ; rotasi (0), (0), (1), (1.57)
    Y2   ; translasi (0.25), (-0.25), (0.042) ; rotasi (0), (0), (1), (1.57)
    Y3   ; translasi (0), (-0.75), (0.042) ; rotasi (0), (0), (1), (0)
    
    Still in the Scene Tree, check the controller assigned to each robot.
     • Blue team uses rcj_soccer_team_blue.py
     • Yellow team uses rcj_soccer_team_yellow.py
     • The ball uses rcj_soccer_ball.py
     • The referee supervisor (listed as a robot in the Scene Tree) uses rcj_soccer_referee_supervisor.py

11. If you need additional Python libraries, such as pandas, math, or OpenCV, open the terminal and install them with a command like this:
    Langkah 1
    cd rcj-soccersim
    
    Langkah 2
    $ pip-compile -o requirements/development.txt requirements/development.in

12. Run the simulation by pressing the Play button.

13. To record a match, go to File > Make Movie. Wait until the match finishes to complete the recording.

14. To view the match history, open Visual Studio Code, select Open Folder, choose the rcj-soccersim folder, then navigate to controllers/rcj_soccer_referee_supervisor. Inside the reflog folder, you’ll find all recorded match logs.

## Development

We are open to contributions! Have a look at our [issues](https://github.com/robocup-junior/rcj-soccersim/issues).
Before you make a pull request, make sure the code is formatted
with `black` and `isort`, and `flake8` issues are fixed.

To do so, follow these steps:

1. Create virtualenv `python3 -m venv venv`
2. Install `pip-tools` by running `pip install pip-tools`
3. Install development modules `pip-sync requirements/development.txt`
4. Setup pre-commit hook `pre-commit install`. This hook will not allow you to
commit in case one of the checkers raises an error.
5. In order format the code, run the formatters in this order
    * `isort .`
    * `black .`
6. Manually fix error raised by `flake8 .`

### Updating dependencies

Dependencies for development are managed by pip-tools. To compile current
dependencies run

```bash
$ pip-compile -o requirements/development.txt requirements/development.in
```

In order to update dependencies, use `--upgrade` switch.

