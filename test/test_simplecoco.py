#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer
from pathlib import Path

# from cocotb.runner import get_runner
from cocotb_xsim.vivado_runner import get_runner

from cocotb.clock import Clock

@cocotb.test()
async def cocotb_a(dut):
    dut.clk.value = 0
    await Timer(300,units='ns')
    dut.clk.value = 1
    await Timer(300,units='ns')
    dut._log.info(f"clock value: {dut.clk.value}")
    dut._log.info("done")


@cocotb.test()
async def cocotb_b(dut):

    cocotb.start_soon( Clock(dut.clk,10,units='ns').start() )
    dut.rst.value = 1
    dut.incr_in.value = 1
    await Timer(20,'ns')
    dut.rst.value = 0
    for i in range(30):
        count_out_val = dut.count_out.value.integer
        dut._log.info(f"Count out value: {count_out_val}, i={i}")
        assert(count_out_val==i)
        await Timer(10,'ns')

    
def test_completetb():
    tb_name = "test_simplecoco"

    proj_path = Path(__file__).resolve().parent
    sources = [proj_path / "counter.sv", proj_path / "project_with_ip/ip/cordic_0/cordic_0.xci"]
    sim = "vivado"
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
        hdl_toplevel_lang=hdl_toplevel_lang,
        waves=True)

if __name__ == "__main__":
    test_completetb()
