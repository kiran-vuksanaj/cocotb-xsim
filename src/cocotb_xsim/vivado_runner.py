
import cocotb.runner

from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, TextIO, Tuple, Type, Union
PathLike = Union["os.PathLike[str]", str]
Command = List[str]
Timescale = Tuple[str, str]

import subprocess
from os import environ


class Vivado(cocotb.runner.Simulator):

    supported_gpi_interfaces = {'verilog': ['xsi']}
    
    @staticmethod
    def _simulator_in_path() -> None:
        if 'XILINX_VIVADO' not in environ:
            raise SystemExit("ERROR: Vivado not found. Run {VIVADO}/settings64.sh if you haven't already.")

        
    def _ip_synth_cmds(self, xci_files: Sequence[PathLike], partNum: Union[str,None] = None) -> Sequence[Command]:
        """
        file-generation + commands in order to synthesize ip for
        """

        if partNum == None:
            partNum = "xc7s50csga324-1"

        # build tiny vivado script to use
        with open(self.build_dir / "build_ip.tcl","w") as f:
            f.write(f"set partNum {partNum}\n")
            f.write("set_part $partNum\n")

            for xci_path in xci_files:
                f.write(f"read_ip {xci_path}\n")
            f.write("export_ip_user_files\n")

        ip_cmds: Sequence[Command] = []
        ip_cmds.append( ['vivado', '-mode', 'batch', '-source', 'build_ip.tcl'] )

        for xci_filename in xci_files:
            xci_as_path = Path(xci_filename)
            ip_name = xci_as_path.stem
            print("IP Name:", ip_name)

            prj_entry_name = Path('.ip_user_files') / 'sim_scripts' / ip_name / 'xsim' / 'vhdl.prj'
            ip_cmds.append( ['xvhdl', '--incr', '--relax', '-prj', str(prj_entry_name)] )
        
        return ip_cmds
        

    def _build_command(self) -> Sequence[Command]:

        cmds = []

        ip_sources = []
        for source in self.sources:
            if cocotb.runner.is_verilog_source(source):
                # TODO maybe should be redone for a .v file ending?
                cmds.append(['xvlog','-sv', str(source)])
            elif cocotb.runner.is_vhdl_source(source):
                cmds.append(['xvhdl', str(source)])
            elif ".xci" in str(source):
                # JANK as fuck
                ip_sources.append(str(source))
            else:
                raise ValueError(
                    f"Unknown file type: {str(source)} can't be compiled."
                )


        cmds.extend( self._ip_synth_cmds(ip_sources) )
        # cmds.append(['vivado', '-mode', 'batch', '-source', 'build_ip.tcl'])
        # cmds.append(['xvhdl', '--incr', '--relax', '-prj', '.ip_user_files/sim_scripts/cordic_0/xsim/vhdl.prj'])
        # cmds.append
        # cmds.append(['xvhdl','--incr', '--relax', '-prj', '/home/kiranv/Documents/fpga/vivgui/getfifos/getfifos.ip_user_files/sim_scripts/cordic_0/xsim/vhdl.prj'])


        self.snapshot_name = "pybound_sim"
            
        elab_cmd = ["xelab",
                    "-top", self.hdl_toplevel,
                    "-snapshot", "pybound_sim",
                    "-debug", "wave",
                    "-dll",
                    "-L","xil_defaultlib"
                    ]
        cmds.append(elab_cmd)

        print("Build Commands: ",cmds)

        return cmds

    def _test_command(self) -> Sequence[Command]:
        # bridge to cross: everything needs to become internalized to a module

        cmd = [
            ["python3", "-m", "cocotb_xsim"]
        ]

        xilinx_root = environ['XILINX_VIVADO']
        self.env["LD_LIBRARY_PATH"] = f"{xilinx_root}/lib/lnx64.o:{xilinx_root}/lib/lnx64.o/Default:"
        self.env["VIVADO_SNAPSHOT_NAME"] = "pybound_sim"

        return cmd

    def _get_parameter_options(self, paramters: Mapping[str, object]) -> Command:
        # TODO make this actually return stuff properly... i think fitting the -generic_top "PARAM=1" format
        return []
        

def get_runner(simulator_name: str) -> cocotb.runner.Simulator:
    """
    this is... pretty jank. manually add 'vivado' to the list of supported sims
    """

    if simulator_name == "vivado":
        return Vivado()
    else:
        return cocotb.runner.get_runner(simulator_name)


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
    
    launch_cmd = ["python3", "-m", "cocotb_xsim"]
    status = subprocess.run(launch_cmd, env=new_env)
    print(f'launch status: {status}')


if __name__=="__main__":
    makefile_recreate()
