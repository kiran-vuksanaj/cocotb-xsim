#!/usr/bin/env python3

# minimally adapted from themperek/cocotb-vivado ; thank you!!

from cocotb_xsim.interface_xsim import XSimInterface, XSI_XSimInterface

from cocotb_xsim.vivado_handles import XsimRootHandle, XsiPortHandle, TimedCbClosure, ValueChangeCbClosure

class XSimManager:

    """
    entity to keep track of a simulation running, advance simulation for each subsequent trigger
    """

    _inst = None
    
    def __init__(self, mode="XSI"):

        interface_type = XSimInterface
        if mode=="XSI":
            interface_type = XSI_XSimInterface

        self.sim = interface_type()
        self.ports = {}
        self._cbqueue = {}
        self._vcqueue = []

    def attempt_valuechange_callbacks(self):
        # print(f"making attempts on {len(self._vcqueue)}")
        for vc in self._vcqueue:
            if vc is not None and vc.change_condition_satisfied():
                vc()
                # print("removing one")
                self._vcqueue.remove(vc)
            # else:
            #     print("No")


    def run(self):
        while len(self._cbqueue) > 0:
            next_time = min(self._cbqueue.keys())
            
            time_to_run = next_time - self.get_sim_time()


            self.sim.advance(time_to_run)
            for cb in self._cbqueue[next_time]:
                if cb is not None:
                    cb()
                # TODO this does not seem comprehensive yet; checking value changes /once/
                self.attempt_valuechange_callbacks()

            self._cbqueue.pop(next_time)

        return False
        
    def get_root_handle(self):
        return XsimRootHandle(self)


    def _init_port_handles(self,port_info):
        out = {}
        for portname in port_info.keys():
            handle = XsiPortHandle(self,portname,port_info[portname][1])
            out[ portname ] = handle
        return out
    
    def start_simulator(self):
        self.sim.launch_simulator()
        self.ports = self._init_port_handles( self.sim.list_port_names() )

    def register_cb(self,t,cb,ud):

        ret = TimedCbClosure(t,cb,ud)

        time_to_fire = self.get_sim_time()+t

        if time_to_fire in self._cbqueue:
            self._cbqueue[time_to_fire].append(ret)
        else:
            self._cbqueue[time_to_fire] = [ret]
        
        return ret
        # print("ud",ud)

    def register_vc_cb(self,handle,callback,edge,ud):
        # print("adding one")
        closure = ValueChangeCbClosure(handle,edge,callback,ud)
        self._vcqueue.append(closure)
        return closure
        

    def get_sim_time(self):
        return self.sim.sim_getsimtime()

    def stop_simulator(self):
        self.sim.stop_simulator()

    @classmethod
    def inst(cls):
        if cls._inst is None:
            raise Exception("Simulation manager not initialized")
        return cls._inst

    @classmethod
    def init(cls):
        cls._inst = XSimManager()
        return cls._inst
