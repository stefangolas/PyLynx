# PyLynx

## About
PyLynx is a command-level Python interface to the Lynx liquid-handling robot by Dynamic Devices. PyLynx works using the TCP/IP interface to the Lynx to communicate with a universal method.

Raise an issue, post on labautomation.io, or contact stefanmgolas@gmail.com if you have any questions.

## VVP Commands

Commands to the 96-channel VVP use Pandas dataframes (with some extra functionality) to specify volumes. This makes it easy to access and modify command data.

To initialize a VVP command array, run
```python
from pylynx import VVPArray
array = VVPArray()
```

Here is the initialized array:
```python
print(array)
    0    1    2    3    4    5    6    7    8    9    10   11
A  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
B  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
C  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
D  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
E  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
F  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
G  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
H  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0
```

This can be modified with standard numpy notation:
```python
array.loc['A':'C',] = 20.0
array.loc[:,8:10] = 30.0
```

```python
print(array)
     0     1     2     3     4     5     6     7     8     9     10    11
A  20.0  20.0  20.0  20.0  20.0  20.0  20.0  20.0  30.0  30.0  30.0  20.0
B  20.0  20.0  20.0  20.0  20.0  20.0  20.0  20.0  30.0  30.0  30.0  20.0
C  20.0  20.0  20.0  20.0  20.0  20.0  20.0  20.0  30.0  30.0  30.0  20.0
D   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0  30.0  30.0  30.0   0.0
E   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0  30.0  30.0  30.0   0.0
F   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0  30.0  30.0  30.0   0.0
G   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0  30.0  30.0  30.0   0.0
H   0.0   0.0   0.0   0.0   0.0   0.0   0.0   0.0  30.0  30.0  30.0   0.0
```

And the dataframe can be run as a VVP command as shown:
```python
lynx.aspirate_96_vvp(plate = plate, array = array)
```

### Normalization
Create a VVPArray of volumes that normalize the concentrations in a plate with the `normalize` function.

```python
data = np.random.randint(1, 11, size=(8, 12))
df = pd.DataFrame(data)
normalization_vols = normalize(df, v1 = 30, c2 = 5)
```

## Example Script

```python
from pylynx import (LynxInterface, get_host_ip, VVPArray, MethodWorktable,
                    list_labware)
import numpy as np
import pandas as pd


data = np.zeros((8, 12))
data[:, :3] = 20
df = pd.DataFrame(data)
array = VVPArray(df)

worktable = MethodWorktable("Demo Workspace")

worktable.clear_worktable()
list_labware("Demo Workspace")
worktable.add_labware_to_location("tips_1", "LXB-96-950F", "Loc_02")
worktable.add_labware_to_location("plate_1", "96 Well Plate", "Loc_04")
worktable.add_labware_to_location("plate_2", "96 Well Plate", "Loc_06")
worktable.save_worktable()


ip = get_host_ip()
lynx = LynxInterface(ip=ip, port=47000, simulating=True)

lynx.setup()


lynx.load_tips(tips="tips_1")
response = lynx.aspirate_96_vvp(plate = "plate_1", array = array)
response = lynx.dispense_96_vvp(plate = "plate_2", array = array)
lynx.eject_tips(tips="tips_1")



lynx.tip_pickup_sv('tips_1', row = 2, column = 5)
lynx.aspirate_sv('plate_1', vol = 30, row = 1, column = 8)
lynx.dispense_sv('plate_1', vol = 30, row = 2, column = 2)
lynx.tip_eject_sv('tips_1', row = 2, column = 5)
```

## Installation instructions:
1. Install 32-bit Python [here](https://www.python.org/downloads/windows/). PyLynx has been tested on Python 3.9+.
2. Install git [here](https://git-scm.com/download/win).
3. Run `git clone https://github.com/stefangolas/PyLynx.git` from the command line
4. Run `cd pylynx`
5. Run `pip install -e .`
6. Set an environment variable called `MM4_DATA_PATH` to point to the directory containing your MM4 workspaces
7. Run `pylynx-configure <Workspace_name>`
8. Run `pylynx-new-project`
9. Run `py example_script.py`

### Common Errors:

**"pip is not recognized as an internal or external command"** </br>
See this stack overflow answer: https://stackoverflow.com/a/23709194

**Errors relating to pip installing pandas** </br>
Try running `pip install pandas==2.0.0`

### Configuration Tool
The `pylynx-configure` tool modifies the universal method to be compatible with the chosen workspace in the following ways:
* Delete method worktable sides (e.g. Left, Right) that don't exist in the workspace
* Delete method commands that are not possible in the workspace
* Delete method worktable resource locations that are not in the workspace

The user must change `utf-16` to `utf-8` in the workspace worktable XML (e.g. `Lynx.Left.Worktable`) manually before running this tool
