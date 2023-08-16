# PyLynx

## About
PyLynx is a command-level Python interface to the Lynx liquid-handling robot by Dynamic Devices. PyLynx works using the TCP/IP interface to the Lynx to communicate with a universal method.

## Example Code

```python
from pylynx import LynxInterface, get_host_ip, ArrayVVP
import numpy as np
import pandas as pd


data = np.zeros((8, 12))
data[:, :3] = 20
df = pd.DataFrame(data)
array = ArrayVVP(df)

# Initialize the Lynx interface
ip = get_host_ip()
lynx = LynxInterface(ip=ip, port=47000, simulating=True)
lynx.setup()

# Assign resources from the worktable
worktable = lynx.load_worktable('test_worktable3.worktable')
tips = worktable.allocate_labware('tips_01')
plate = worktable.allocate_labware('plate_01')

# Run liquid-handling commands
lynx.load_tips(tips = tips)
response = lynx.aspirate_96_vvp(plate = plate, channel_data = channel_data)
response = lynx.dispense_96_vvp(plate = plate, channel_data = channel_data)
lynx.eject_tips(tips = tips)

```

## Installation instructions:
1. Install 32-bit Python [here](https://www.python.org/downloads/windows/). PyLynx has been tested on Python 3.9+.
2. Install git [here](https://git-scm.com/download/win).
3. Run `git clone https://github.com/stefangolas/PyLynx.git` from the command line
4. Run `cd pylynx`
5. Run `pip install -e .`
6. Run `pylynx-configure`
7. Make a directory outside of the pylynx folder and `cd` into that
8. Run `pylynx-new-project`
9. Run `py example_script.py`
