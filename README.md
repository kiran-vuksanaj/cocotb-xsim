## Cocotb + Vivado XSim

Following closely in the footsteps of themperek's [cocotb-vivado](github.com/themperek/cocotb-vivado)


### Getting things running
* make sure you have Python installed in such a way that libpython / the `<Python.h>` file exists; from `apt`, this might look like installing `python3-dev`. If you have cocotb running, this should already be handled.
* make sure you have Vivado (2024.2 is what I've been building for) installed, and its paths etc. added to your terminal: your `.bashrc` might need a line like
``` sh
source /tools/Xilinx/Vivado/2024.2/settings64.sh
```
(modified if you have Vivado stored in a different place)
* make a virtual environment with cocotb in it (only need to do once)

``` sh
python3 -m venv venv
source venv/bin/activate
pip3 install -e .
```
* run the tests here:

``` sh
pytest -s test/
```

### submodules here
TODO diagram + descriptions of operations (compare between normal cocotb and this)


### Upcoming things to work on
- ~~organize into directories properly~~, make more tests
- ~~python test runner object~~
- Make rising/falling edge triggers in the manager
- restore proper management of undefined variables
- Build second backend for launching a TCL shell for the simulator and interacting with Vivado through that
- Export to vcd files
- simplified way to go from Vivado IP to cocotb simulation
