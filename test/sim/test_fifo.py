#!/usr/bin/env python3

import cocotb
from cocotb.triggers import Timer, RisingEdge, ClockCycles, ReadOnly
from cocotb.clock import Clock






@cocotb.test()
async def clocked_fifo(dut):

    cocotb.start_soon( Clock(dut.clk, 10, units='ns').start() )


    await Timer(2000,units='ps')









from cocotb_xsim.vivado_runner import get_runner
from pathlib import Path

def test_fifotb():

    file_path = Path(__file__).resolve()

    tb_name = file_path.stem
    proj_path = file_path.parent.parent
    sources = [proj_path / "ip/fifo_dut_sync/fifo_dut_sync.xci",
               proj_path / "hdl" / "fifo_wrap.sv"
               ]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "fifo_wrap"

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
    test_fifotb()
