import cocotb.runner
import Xsi_Loader

class Vivado(cocotb.runner.Runner):
    def __init__(self):
        print("hi")

def get_runner(simulator_name):

    if simulator_name == 'vivado':
        return Vivado()
    return cocotb.runner.get_runner()
