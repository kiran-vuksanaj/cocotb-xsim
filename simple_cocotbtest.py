#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer

from cocotb.runner import get_runner

@cocotb.test()
async def test_a(dut):
    dut.clk.value = 0
    await Timer(300,units='ns')
    dut.clk.value = 1
    await Timer(300,units='ns')
    print(dut.clk.value)
    print("done")


def icarus_reference_testbench():
    tb_name = "simple_cocotbtest"
    sources = ["counter.sv"]
    sim = "icarus"
    hdl_toplevel_lang = "verilog"
    toplevel = "counter"
    runner = get_runner(sim)

    runner.build(
        sources=sources,
        hdl_toplevel=toplevel,
        always=True,
        timescale = ('1ns','1ps'),
        waves=True)
    runner.test(
        hdl_toplevel=toplevel,
        test_module=tb_name,
        waves=True)

if __name__ == "__main__":
    icarus_reference_testbench()
