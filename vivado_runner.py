
from cocotb.runner import Simulator

from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, TextIO, Tuple, Type, Union
PathLike = Union["os.PathLike[str]", str]
Command = List[str]
Timescale = Tuple[str, str]

import subprocess
from os import environ


class Vivado(Simulator):

    supported_gpi_interfaces = {'verilog': ['xsi']}
    
    @staticmethod
    def _simulator_in_path() -> None:
        if 'XILINX_VIVADO' not in environ:
            raise SystemExit("ERROR: Vivado not found. Run {VIVADO}/settings64.sh if you haven't already.")

    def _build_command(self) -> Sequence[Command]:

        cmds = []
        for source in self.sources:
            if not is_verilog_source(source):
                raise ValueError(
                    f"So far, only supporting verilog sources. {str(source)} can't be compiled."
                )
            # TODO maybe should be redone for a .v file ending?
            cmds.append(['xvlog','-sv', str(source)])


        self.snapshot_name = "pybound_sim"
            
        elab_cmd = ["xelab",
                    "-top", self.hdl_toplevel,
                    "-snapshot", "pybound_sim",
                    "-debug", "wave",
                    "-dll'"
                    ]
        cmds.append(elab_cmd)

        return cmds

    def _test_command(self) -> Sequence[Command]:
        # bridge to cross: everything needs to become internalized to a module
        raise NotImplementedError()
        




def makefile_recreate():
    """
    match what the makefile does, so as to motivate the proper functions for the runner type
    """

    sources = ["counter.sv", "counter_tb.sv"]

    toplevel = "counter"
    snapshot_name = "pybound_sim"

    module = "simple_cocotbtest"

    for source in sources:
        compile_source_cmd = ["xvlog", "-sv", source]
        status = subprocess.run(compile_source_cmd)
        print(f'compile {source} status: {status}')

    elab_cmd = ["xelab", "-top", toplevel, "-snapshot", snapshot_name, "-debug", "wave", "-dll"]
    status = subprocess.run(elab_cmd)
    print(f'elaborate status: {status}')

    new_env = environ
    xilinx_root = environ["XILINX_VIVADO"]
    new_env["LD_LIBRARY_PATH"] = f"{xilinx_root}/lib/lnx64.o:{xilinx_root}/lib/lnx64.o/Default:"
    new_env["SNAPSHOT_NAME"] = "pybound_sim"
    new_env["MODULE"] = module
    
    launch_cmd = ["python3", "__init__.py"]
    status = subprocess.run(launch_cmd, env=new_env)
    print(f'launch status: {status}')


if __name__=="__main__":
    makefile_recreate()
