import cocotb
from cocotb.triggers import Timer


from pathlib import Path
# from cocotb.runner import get_runner
from cocotb_xsim.vivado_runner import get_runner

from cocotb.clock import Clock


@cocotb.test()
async def simple_timers(dut):
    cocotb.start_soon( Clock(dut.aclk,10,units='ns').start() )
    dut.s_axis_cartesian_tvalid.value = 0
    dut.s_axis_cartesian_tdata.value = 1

    await Timer(20,units='ns')
    dut.s_axis_cartesian_tvalid.value = 1
    await Timer(10,units='ns')
    dut.s_axis_cartesian_tvalid.value = 0
    await Timer(2000,units='ns')
    dut._log.info(f"Output: 0x{dut.m_axis_dout_tdata.value.integer:x}")
    dut.s_axis_cartesian_tvalid.value = 0
    await Timer(30000,units='ns')
    dut._log.info("done")
    


def test_cordictb():
    tb_name = "test_cordic"
    proj_path = Path(__file__).resolve().parent
    sources = [proj_path / "../hdl/cordic_wrap.sv", proj_path / "../ip/cordic_0/cordic_0.xci"]
    sim = "vivado"
    hdl_toplevel_lang = "verilog"
    toplevel = "cordic_wrap"
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
        hdl_toplevel_lang="verilog",
        waves=True)

if __name__ == "__main__":
    test_cordictb()
