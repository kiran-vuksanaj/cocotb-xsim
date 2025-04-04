import os
import ctypes

# heavily inspired by themperek/cocotb-vivado; thank you!!

class Xsi_Loader:
    """
    Class for
    
    """
    xsiNumTopPorts = 1
    xsiTimePrecisionKernel = 2
    xsiDirectionTopPort = 3
    xsiHDLValueSize = 4
    xsiNameTopPort = 5

    def __init__(self):
        self.load_libraries()

        self.handle = ctypes.c_void_p(None)
    
    def load_libraries(self):

        snapshot_name = os.getenv("SNAPSHOT_NAME")

        design_so_file = "xsim.dir/{snapshot_name}/xsimk.so".format(snapshot_name=snapshot_name)

        kernel_so_file = "libxv_simulator_kernel.so"
        self.kernel_lib = ctypes.CDLL(kernel_so_file)
        self.design_lib = ctypes.CDLL(design_so_file)

        Xsi_H.define_lib( self.design_lib, Xsi_H.design_lib_defines )
        Xsi_H.define_lib( self.kernel_lib, Xsi_H.kernel_lib_defines )


    def open_handle(self,logFileName,wdbFileName,trace=True):


        # setup_info = Xsi_H.s_xsi_setup_info(logFileName,wdbFileName)
        setup_info = Xsi_H.s_xsi_setup_info(None,None)

        self.handle = self.design_lib.xsi_open( ctypes.pointer(setup_info) )

        # i dont really understand why this needs to be re-wrapped, and it concerns me
        self.handle = Xsi_H.xsiHandle( self.handle )
        
        if trace:
            self.kernel_lib.xsi_trace_all( self.handle )


    def close(self):
        self.kernel_lib.xsi_close( self.handle )

    def run(self,steps):
        step_count = ctypes.c_int64(steps)
        self.kernel_lib.xsi_run( self.handle, step_count )

    def get_value(self,port_number):

        value_space = Xsi_H.s_xsi_vlog_logicval(0,0)
        value_pointer = ctypes.pointer(value_space)

        port_number = ctypes.c_int(port_number)

        self.kernel_lib.xsi_get_value( self.handle, port_number, value_pointer )
        return value_space.aVal

    def put_value(self,port_number,value):

        value_space = Xsi_H.s_xsi_vlog_logicval(value,0)
        value_pointer = ctypes.pointer(value_space)

        port_number = ctypes.c_int(port_number)
        self.kernel_lib.xsi_put_value( self.handle, port_number, value_pointer )

    def get_port_name(self,port_number):
        """ this doesn't exist in the documentation??? does that mean itll disappear?"""
        port_number = ctypes.c_int(port_number)
        name_bytes_p = self.kernel_lib.xsi_get_port_name( self.handle, port_number )

        if name_bytes_p is not None:
            return name_bytes_p.decode('utf-8')
        else:
            return None

    def get_port_number(self,port_name):
        port_name = bytes(port_name,'utf-8')
        return self.kernel_lib.xsi_get_port_number( self.handle, port_name )

    def get_status(self):
        val = self.kernel_lib.get_status( self.handle )
        return val

    def get_time(self):
        time = self.kernel_lib.xsi_get_time( self.handle )
        return time

    def get_port_size(self,port_number):
        port_size = self.kernel_lib.xsi_get_int_port( self.handle, port_number, Xsi_Loader.xsiHDLValueSize )
        return port_size
    
    # trace_all
    # get_error_info
    # isopen
    # restart


class Xsi_H:
    """
    ctypes structs and types to match the "xsi.h" file, and allow interactions with the key functions
    see file $XILINX_VIVADO/data/xsim/include/xsi.h to reference
    """

    class t_xsi_setup_info(ctypes.Structure):
        _fields_ = [("logFileName",ctypes.c_char_p),
                    ("wdbFileName",ctypes.c_char_p),
                    ("xsimDir",ctypes.c_char_p)
                    ]
    class s_xsi_setup_info(t_xsi_setup_info):
        def __init__(self,logFileName,wdbFileName,xsimDir=""):
            if logFileName is not None:
                logFileName = bytes(logFileName,'utf-8')
            if wdbFileName is not None:
                wdbFileName = bytes(wdbFileName,'utf-8')
            if xsimDir is not None:
                xsimDir = bytes(xsimDir,'utf-8')

            super().__init__(logFileName,wdbFileName,xsimDir)
            
    p_xsi_setup_info = ctypes.POINTER(t_xsi_setup_info)

    class s_xsi_vlog_logicval(ctypes.Structure):
        _fields_ = [("aVal",ctypes.c_uint32),
                    ("bVal",ctypes.c_uint32)]

    p_xsi_vlog_logicval = ctypes.POINTER(s_xsi_vlog_logicval)
    xsiHandle = ctypes.c_void_p

    design_lib_defines = {
        'xsi_open': (
            (p_xsi_setup_info,),
            xsiHandle
        )
    }

    kernel_lib_defines = {
        'xsi_run': (
            (xsiHandle, ctypes.c_int64),
            None
            ),
        'xsi_close': (
            (xsiHandle,),
            None
            ),
        'xsi_trace_all': (
            (xsiHandle,),
            None
            ),
        'xsi_get_port_number': (
            (xsiHandle, ctypes.c_char_p),
            ctypes.c_int
            ),
        'xsi_get_port_name': (
            (xsiHandle, ctypes.c_int),
            (ctypes.c_char_p)
        ),
        'xsi_put_value': (
            (xsiHandle, ctypes.c_int, ctypes.c_void_p),
            None
            ),
        'xsi_get_value': (
            (xsiHandle, ctypes.c_int, ctypes.c_void_p),
            None
            ),
        'xsi_get_status': (
            (xsiHandle,),
            ctypes.c_int
            ),
        'xsi_get_time': (
            (xsiHandle,),
            ctypes.c_int
        ),
        'xsi_get_int_port': ( # god i literally don't see docs for this anywhere??
            (xsiHandle,ctypes.c_int,ctypes.c_int),
            ctypes.c_int
        )

    }

    def define_lib(lib,lib_defines):
        """ load argtype and restype into library after it's been opened, according to a dictionary of types"""
        for key in lib_defines:
            lib_fn = getattr(lib,key)
            fn_header = lib_defines[key]
            lib_fn.argtypes = fn_header[0]
            lib_fn.restype = fn_header[1]
        

