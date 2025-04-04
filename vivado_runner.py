# import cocotb.runner

# class Vivado(cocotb.runner.Runner):
#     def __init__(self):
#         print("hi")

# def get_runner(simulator_name):

#     if simulator_name == 'vivado':
#         return Vivado()
#     return cocotb.runner.get_runner()


import subprocess
from os import environ


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
