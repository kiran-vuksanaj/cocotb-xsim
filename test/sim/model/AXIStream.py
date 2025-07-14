#!/usr/bin/env python3

from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor

from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles, ReadOnly

class AXISMonitor(BusMonitor):
    """
    monitors axi streaming bus
    """
    transactions = 0
    def __init__(self, dut, name, clk):
        self._signals = ['axis_tvalid','axis_tready','axis_tdata','axis_tlast']
        BusMonitor.__init__(self, dut, name, clk)
        self.clock = clk
        self.transactions = 0
    async def _monitor_recv(self):
        """
        Monitor receiver
        """
        rising_edge = RisingEdge(self.clock) # make these coroutines once and reuse
        falling_edge = FallingEdge(self.clock)
        read_only = ReadOnly() #This is
        while True:
            await rising_edge
            await falling_edge #sometimes see in AXI shit
            await read_only  #readonly (the postline)
            valid = self.bus.axis_tvalid.value
            ready = self.bus.axis_tready.value
            last = self.bus.axis_tlast.value
            data = self.bus.axis_tdata.value
            if valid and ready:
              self.transactions += 1
              thing = dict(data=data.value,last=last.value,name=self.name,count=self.transactions)
              self.log.info(thing)
              self._recv(thing)


class AXISDriver(BusDriver):
    def __init__(self, dut, name, clk):
        self._signals = ['axis_tvalid', 'axis_tready', 'axis_tlast', 'axis_tdata']
        BusDriver.__init__(self, dut, name, clk)
        self.clock = clk
        self.bus.axis_tdata.value = 0
        self.bus.axis_tlast.value = 0
        self.bus.axis_tvalid.value = 0

    async def _driver_send(self, value, sync=True):
        rising_edge = RisingEdge(self.clock) # make these coroutines once and reuse
        falling_edge = FallingEdge(self.clock)
        read_only = ReadOnly()

        last_val = value['last']
        data_val = value['data']
        
        if sync:
            await rising_edge
            await falling_edge

        self.bus.axis_tvalid.value = 1
        self.bus.axis_tlast.value = last_val
        self.bus.axis_tdata.value = data_val

        ready = self.bus.axis_tready.value

        while not ready:
            await falling_edge
            ready = self.bus.axis_tready.value
        await falling_edge
        self.bus.axis_tvalid.value = 0
