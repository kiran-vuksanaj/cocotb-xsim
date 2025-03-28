#!/usr/bin/env python3

# minimally adapted from themperek/cocotb-vivado ; thank you!!

from interface_xsim import XSimInterface, XSI_XSimInterface

from vivado_handles import XsimRootHandle, XsiPortHandle, CbClosure

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


    def run(self):
        while len(self._cbqueue) > 0:
            next_time = min(self._cbqueue.keys())
            
            time_to_run = next_time - self.get_sim_time()


            self.sim.advance(time_to_run)
            for cb in self._cbqueue[next_time]:
                if cb is not None:
                    cb()

            self._cbqueue.pop(next_time)

        return False
        
    def get_root_handle(self):
        return XsimRootHandle(self)


    def _init_port_handles(self,port_info):
        out = {}
        for port in port_info:
            handle = XsiPortHandle(self,port[0],port[1])
            out[ port[0] ] = handle
        return out
    
    def start_simulator(self):
        self.sim.launch_simulator()
        self.ports = self._init_port_handles( self.sim.list_port_names() )

    def register_cb(self,t,cb,ud):

        ret = CbClosure(t,cb,ud)

        time_to_fire = self.get_sim_time()+t

        if time_to_fire in self._cbqueue:
            self._cbqueue[time_to_fire].append(ret)
        else:
            self._cbqueue[time_to_fire] = [ret]
        
        return ret
        # print("ud",ud)
        
        

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
