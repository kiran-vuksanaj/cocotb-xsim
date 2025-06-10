#!/usr/bin/env python3
# minimally adapted from themperek/cocotb-vivado ; thank you!!

MODULE = 0
REG = 2

import abc
from collections.abc import Callable
from typing import Dict, List, Mapping, Optional, Sequence, TextIO, Tuple, Type, Union, Any


class XsimRootHandle(object):
    def __init__(self, mgr):
        self.mgr = mgr

    def get_const(self):
        return True

    def get_type(self):
        return MODULE

    def get_name_string(self):
        return "top"

    def get_type_string(self):
        return "MODULE"

    def get_definition_name(self):
        return ""

    def get_definition_file(self):
        return ""

    def iterate(self, nothing):
        pass
        # for name in self.mgr.ports:
        #     yield self.mgr.ports[name]

    def get_handle_by_name(self, name):
        if name not in self.mgr.ports:
            return

        return self.mgr.ports[name]

class XsiPortHandle(object):
    def __init__(self, mgr, name, size):
        self.name = name

        self.size = size
        self.mgr = mgr

    def get_const(self):
        return False

    def get_type(self):
        return REG

    def get_name_string(self):
        return self.name

    def get_type_string(self):
        return "REG"

    def get_definition_name(self):
        return ""

    def get_definition_file(self):
        return ""

    def get_num_elems(self):
        return self.size

    def get_range(self):
        return (self.size - 1, 0)

    def set_signal_val_int(self, action, value):
        # also what does action do?
        str_value = f"{value:0{self.size}b}"
        self.mgr.sim.sim_setvalue(self.name, str_value)

    def set_signal_val_binstr(self, action, value):
        self.mgr.sim.sim_setvalue(self.name, value)

    def get_signal_val_binstr(self):
        value = self.mgr.sim.sim_getvalue(self.name)
        # this should return a binstr
        return value
        # format_str = "{value:0"+str(self.size)+"b}"
        # binstr = format_str.format(value=value)
        # return binstr

    def get_signal_val_int(self):
        value = self.mgr.sim.sim_getvalue(self.name)
        return value

class CbClosure(abc.ABC):
    def __init__(self) -> None:
        self.cb: Union[Callable[[Any],None],None] = None
        self.ud: Any = None

    def __call__(self):
        if self.cb is not None:
            self.cb(self.ud)

    def deregister(self):
        self.cb = None

class TimedCbClosure(CbClosure):
    def __init__(self, time_off, cb, ud):
        self.time_off = time_off
        self.cb = cb
        self.ud = ud
        self.cb_id = 1

class ValueChangeCbClosure(CbClosure):

    def __init__(self, handle, edge, cb, ud):
        self.handle = handle
        self.cb = cb
        self.ud = ud
        self.edge = edge

        self.previous_value = handle.get_signal_val_int()

    def change_condition_satisfied(self):
        current_value = self.handle.get_signal_val_int()
        # print(f"Change condition satisfied? {self.previous_value}, {current_value}, {self.handle}, {self.edge}")
        if self.edge == 1:
            out = current_value > self.previous_value
        else:
            out = current_value < self.previous_value

        self.previous_value = current_value
        return out
