
import cocotb.runner

from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, TextIO, Tuple, Type, Union
PathLike = Union["os.PathLike[str]", str]
Command = List[str]
Timescale = Tuple[str, str]

import subprocess
from os import environ

import csv


class Vivado(cocotb.runner.Simulator):

    supported_gpi_interfaces = {'verilog': ['xsi'], 'vhdl': ['xsi']}

    def __init__(self,mode):
        self.launch_mode = mode
        super().__init__()
    
    @staticmethod
    def _simulator_in_path() -> None:
        if 'XILINX_VIVADO' not in environ:
            raise SystemExit("ERROR: Vivado not found. Run {VIVADO}/settings64.sh if you haven't already.")

    def _file_info_to_parse(self, file_info,working_dir):
        """
        converts list of traits as written in a "file_info.txt" file to a command to compile the file

        """
        if(len(file_info) == 5):
             filename, language, output_lib, filepath, include_dirs = file_info
        else:
            filename, language, output_lib, filepath = file_info
            include_dirs = ""
        cmd = []

        language = language.lower()
        if language == "systemverilog":
            cmd += ['xvlog', '-sv']
        elif language == "verilog":
            cmd += ['xvlog']
        elif language == "vhdl":
            cmd += ['xvhdl']

        cmd += ['-work',f'{output_lib}=xsim.dir/{output_lib}']

        absolute_path = working_dir / filepath

        if "/tools/Xilinx" in filepath:
            real_start = filepath.index("/tools/Xilinx")
            filepath = filepath[real_start:]
            absolute_path = Path(filepath)
        
        absolute_path = absolute_path.resolve()
        cmd += [str(absolute_path)]

        if (language != "vhdl"):
            include_dirs = include_dirs.split("incdir=")
            for dirname in include_dirs:
                dirname = dirname.strip('\'"')
                if (len(dirname)>0):
                    absolute_path = working_dir / dirname
                    absolute_path = absolute_path.resolve()

                    cmd += ['-i', str(absolute_path)]

        # print(cmd)
        return cmd
        

    def _outofdate_ip(self,xci_files: Sequence[PathLike]) -> Sequence[PathLike]:

        # if self.always:
        #     return xci_files

        outofdate = []
        
        for xci_file in xci_files:

            xci_file = Path(xci_file).resolve()
            ip_name = xci_file.stem
            sample_ip_user_file = self.build_dir / ".ip_user_files" / "sim_scripts" / ip_name / "xsim" / "README.txt"

            if cocotb.runner.outdated(sample_ip_user_file,[xci_file]):
                outofdate.append(xci_file)

        print("Out Of Date: ",outofdate)
        return outofdate
        
    def _ip_synth_cmds(self, xci_files: Sequence[PathLike], partNum: Union[str,None] = None) -> Sequence[Command]:
        """
        file-generation + commands in order to synthesize ip for
        """

        if partNum == None:
            partNum = "xc7s50csga324-1"

        # build tiny vivado script to usep

        ip_cmds: Sequence[Command] = []

        outdated_xci_files = self._outofdate_ip(xci_files)

        if (len(outdated_xci_files) > 0):
            with open(self.build_dir / "build_ip.tcl","w") as f:
                f.write(f"set partNum {partNum}\n")
                f.write("set_part $partNum\n")

                for xci_path in outdated_xci_files:
                    f.write(f"read_ip {xci_path}\n")
                f.write("export_ip_user_files\n")
            self._execute( [['vivado', '-mode', 'batch', '-source', 'build_ip.tcl']], cwd=self.build_dir)


        for xci_filename in xci_files:
            xci_as_path = Path(xci_filename)
            ip_name = xci_as_path.stem
            print("IP Name:", ip_name)

            ip_user_root = self.build_dir / '.ip_user_files'

            # ipstatic = ip_user_root / 'ipstatic' / 'ip'
            # for child in ipstatic.iterdir():
            #     if child.is_dir():
            #         dir_to_include = child / 'hdl'
            #         self.includes.append(str(dir_to_include))

            vcs_script_root = ip_user_root / 'sim_scripts' / ip_name / 'vcs'
            vcs_file_info = vcs_script_root / 'file_info.txt'

            with open(str(vcs_file_info),newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    library_name = row[2]
                    self.xilinx_libraries.add( library_name )
            self.xilinx_libraries.add( 'xpm' )
            self.xilinx_libraries.add( 'secureip' )

            xsim_script_root = ip_user_root / 'sim_scripts' / ip_name / 'xsim'

            xsim_file_info = xsim_script_root / 'file_info.txt'
            with open(str(xsim_file_info),newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    module_name = row[0]
                    library_name = row[2]
                    module_name = module_name[:module_name.index('.')]
                    self.elab_modules.append(f"{library_name}.{module_name}")
                    # ip_cmds.append ( self._file_info_to_parse(row,xsim_script_root) )

            
            vhdl_proj = xsim_script_root / 'vhdl.prj'
            vlog_proj = xsim_script_root / 'vlog.prj'

            if vhdl_proj.exists():
                print("VHDL project EXISTS!")
                ip_cmds.append( ['xvhdl','--incr','--relax','-prj',str(vhdl_proj)] + self._get_include_options(self.includes) )
            else:
                print("NO VHDL")
            if vlog_proj.exists():
                print("VERILOG PROJECT EXISTS!")
                ip_cmds.append( ['xvlog','--incr','--relax','-prj',str(vlog_proj)] + self._get_include_options(self.includes) )
            else:
                print("no VERILOG")

            # ip_cmds.append( ['sh','-c', f"cd {xsim_script_root} && ./{ip_name}.sh -step compile"] )

        return ip_cmds

    def _get_include_options(self, includes):
        out = []
        for incl in includes:
            out.extend(['-i',str(incl)])
        return out

    def _build_command(self) -> Sequence[Command]:

        self.xilinx_libraries = set()
        self.elab_modules = []
        
        cmds = []

        ip_sources = []
        for source in self.sources:
            if cocotb.runner.is_verilog_source(source):
                # TODO maybe should be redone for a .v file ending?
                cmds.append(['xvlog','-sv', str(source)] + self._get_include_options(self.includes))
            elif cocotb.runner.is_vhdl_source(source):
                cmds.append(['xvhdl', str(source)] + self._get_include_options(self.includes))
            elif ".xci" in str(source):
                # JANK as fuck
                ip_sources.append(str(source))
            else:
                raise ValueError(
                    f"Unknown file type: {str(source)} can't be compiled."
                )


        if len(ip_sources) > 0:
            cmds.extend( self._ip_synth_cmds(ip_sources) )
        # cmds.append(['vivado', '-mode', 'batch', '-source', 'build_ip.tcl'])
        # cmds.append(['xvhdl', '--incr', '--relax', '-prj', '.ip_user_files/sim_scripts/cordic_0/xsim/vhdl.prj'])
        # cmds.append
        # cmds.append(['xvhdl','--incr', '--relax', '-prj', '/home/kiranv/Documents/fpga/vivgui/getfifos/getfifos.ip_user_files/sim_scripts/cordic_0/xsim/vhdl.prj'])


        self.snapshot_name = "pybound_sim"

        elab_cmd = ["xelab",
                    "-top", self.hdl_toplevel,
                    "-snapshot", "pybound_sim",
                    ] + self._get_include_options(self.includes)

        # for elab_module in self.elab_modules:
        #     if (elab_module==self.hdl_toplevel or elab_module==f"work.{self.hdl_toplevel}"):
        #         self.elab_modules.remove(elab_module)

        elab_cmd.extend(self.elab_modules)

        for library_name in self.xilinx_libraries:
            elab_cmd.extend(['-L',library_name])
        
        if (self.launch_mode == 'XSI'):
            elab_cmd.extend(['-dll','-debug','wave'])
        else:
            elab_cmd.extend(['-debug','all'])
        
        cmds.append(elab_cmd)

        print("Build Commands: ",cmds)

        return cmds

    def _test_command(self) -> Sequence[Command]:
        # bridge to cross: everything needs to become internalized to a module

        cmd = [
            ["python3", "-m", "vicoco"]
        ]

        xilinx_root = environ['XILINX_VIVADO']
        self.env["LD_LIBRARY_PATH"] = f"{xilinx_root}/lib/lnx64.o:{xilinx_root}/lib/lnx64.o/Default:"
        self.env["VIVADO_SNAPSHOT_NAME"] = "pybound_sim"
        self.env["TOPLEVEL_LANG"] = self.hdl_toplevel_lang
        self.env["XSIM_INTERFACE"] = self.launch_mode

        return cmd

    def _get_parameter_options(self, paramters: Mapping[str, object]) -> Command:
        # TODO make this actually return stuff properly... i think fitting the -generic_top "PARAM=1" format
        return []
        

def get_runner(simulator_name: str) -> cocotb.runner.Simulator:
    """
    this is... pretty jank. manually add 'vivado' to the list of supported sims
    """

    if simulator_name == "vivado":
        return Vivado('XSI')
    elif simulator_name == "vivado_tcl":
        return Vivado('TCL')
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
    
    launch_cmd = ["python3", "-m", "vicoco"]
    status = subprocess.run(launch_cmd, env=new_env)
    print(f'launch status: {status}')


if __name__=="__main__":
    makefile_recreate()
