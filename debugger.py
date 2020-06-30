from pyedbglib.hidtransport.hidtransportfactory import hid_transport
from pyedbglib.protocols import housekeepingprotocol
from pyedbglib.protocols import housekeepingprotocol
from pyedbglib.protocols import avr8protocol
from pyedbglib.protocols import avr8protocolerrors

# Retrieve device info
from pymcuprog.deviceinfo import deviceinfo

# Construct an NVM provider
from pymcuprog.nvmupdi import NvmAccessProviderCmsisDapUpdi

import logging

# Start session
#avr.start()

logging.basicConfig(level=logging.INFO,handlers=[logging.StreamHandler()])

class Debugger():

    def __init__(self, DeviceName):
        # Make a connection
        self.transport = hid_transport()
        self.transport.disconnect()
        # Connect
        self.transport.connect()
        self.deviceInf = deviceinfo.getdeviceinfo(DeviceName)
        self.memoryinfo = deviceinfo.DeviceMemoryInfo(self.deviceInf)
        self.device = NvmAccessProviderCmsisDapUpdi(self.transport, self.deviceInf)
        self.device.avr.deactivate_physical()
        self.device.avr.activate_physical()
        # Start debug by attaching (live)
        self.device.avr.protocol.attach()
    
    # Memory interaction (SRAM)
    def writeMemory(self, address, data):
        #self.detach()
        return self.device.write(self.memoryinfo.memory_info_by_name('internal_sram'), 0, 64)

    def readMemory(self, address, numBytes):
        #self.detach()
        return self.device.read(self.memoryinfo.memory_info_by_name('internal_sram'), 0, 64)
    
    # General debugging

    def attach(self):
        self.device.avr.protocol.attach()

    def detach(self):
        self.device.avr.protocol.detach()

    # Flow controll
    def reset(self):
        self.device.avr.protocol.reset()
    
    def step(self):
        self.device.avr.protocol.step() 
    
    def stop(self):
        self.device.avr.protocol.stop()

    def run(self):
        self.device.avr.protocol.run()

    def runTo(self, address):
        self.device.avr.protocol.run_to(address)

    # Register and programcounter
    def readRegs(self):
        return self.device.avr.protocol.regfile_read()

    def writeRegs(self, regs):
        return self.device.avr.protocol.regile_write(regs)

    def readProgramCounter(self):
        self.device.avr.protocol.program_counter_read()

    def writeProgramCounter(self, programCounter):
        self.device.avr.protocol.program_counter_write(programCounter)

    # SoftwareBreakpoints
    def breakpointSWSet(self, address):
        self.device.avr.protocol.software_breakpoint_set(address)
    
    def breakpointSWClear(self, address):
        self.device.avr.protocol.software_breakpoint_clear(address)

    def breakpointSWClearAll(self):
        self.device.avr.protocol.software_breakpoint_clear_all()
    
    def breakpointHWSet(self, address):
        self.device.avr.breakpoint_set(address)

    def breakpointHWClear(self):
        self.device.avr.breakpoint_clear()
    
    # Cleanup code for detatching target
    def cleanup(self):
        # and end debug
        self.device.avr.protocol.detach()
        # Stop session
        #avr.stop()
        self.device.avr.deactivate_physical()
        # Unwind the stack
        self.transport.disconnect()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.cleanup()

