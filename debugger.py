from pyedbglib.hidtransport.hidtransportfactory import hid_transport
from pyedbglib.protocols import housekeepingprotocol
from pyedbglib.protocols import housekeepingprotocol
from pyedbglib.protocols import avr8protocol
from pyedbglib.protocols import avr8protocolerrors

# Retrieve device info
from pymcuprog.deviceinfo import deviceinfo

# Construct an NVM provider
from pymcuprog.nvmupdi import NvmAccessProviderCmsisDapUpdi

from pyedbglib.protocols.avrcmsisdap import AvrCommand, AvrCommandError

import logging
import threading
import time
import asyncio

# Start session
#avr.start()

logging.basicConfig(level=logging.INFO,handlers=[logging.StreamHandler()])

lock = asyncio.Lock()

async def pollingThread(eventReciver: AvrCommand):
    reciver = eventReciver
    while True:
        async with lock:
            logging.info(reciver.poll_events())

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
        self.eventReciver = AvrCommand(self.transport)
        self.device.avr.deactivate_physical()
        self.device.avr.activate_physical()
        # Start debug by attaching (live)
        self.device.avr.protocol.attach()
        threading.Thread(target=pollingThread, args=(self.eventReciver,)).start()
    
    async def pollEvent(self):
        logging.info(self.eventReciver.poll_events())

    # Memory interaction
    async def writeSRAM(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('internal_sram'))['address']
        async with lock:
            return self.device.write(self.memoryinfo.memory_info_by_name('internal_sram'), address-offset, data)

    async def readSRAM(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('internal_sram'))['address']
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('internal_sram'), address-offset, numBytes)

    async def readFlash(self, address, numBytes):
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('flash'), address, numBytes)

    async def writeEEPROM(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('eeprom'))['address']
        async with lock:
            return self.device.write(self.memoryinfo.memory_info_by_name('eeprom'), address-offset, data)

    async def readEEPROM(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('eeprom'))['address']
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('eeprom'), address-offset, numBytes)

    async def writeFuse(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('fuses'))['address']
        async with lock:
            return self.device.write(self.memoryinfo.memory_info_by_name('fuses'), address-offset, data)

    async def readFuse(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('fuses'))['address']
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('fuses'), address-offset, numBytes)

    async def writeLock(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('lockbits'))['address']
        async with lock:
            return self.device.write(self.memoryinfo.memory_info_by_name('lockbits'), address-offset, data)

    async def readLock(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('lockbits'))['address']
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('lockbits'), address-offset, numBytes)

    async def writeSignature(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('signatures'))['address']
        async with lock:
            return self.device.write(self.memoryinfo.memory_info_by_name('signatures'), address-offset, data)

    async def readSignature(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('signatures'))['address']
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('signatures'), address-offset, numBytes)

    async def writeUserSignature(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('user_row'))['address']
        async with lock:
            return self.device.write(self.memoryinfo.memory_info_by_name('user_row'), address-offset, data)

    async def readUserSignature(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('user_row'))['address']
        async with lock:
            return self.device.read(self.memoryinfo.memory_info_by_name('user_row'), address-offset, numBytes)

    # General debugging

    async def attach(self):
        async with lock:
            self.device.avr.protocol.attach()

    async def detach(self):
        async with lock:
            self.device.avr.protocol.detach()

    # Flow controll
    async def reset(self):
        async with lock:
            self.device.avr.protocol.reset()
    
    async def step(self):
        async with lock:
            self.device.avr.protocol.step() 
    
    async def stop(self):
        async with lock:
            self.device.avr.protocol.stop()

    async def run(self):
        async with lock:
            self.device.avr.protocol.run()

    async def runTo(self, address):
        async with lock:
            self.device.avr.protocol.run_to(address)

    async def readStackPointer(self):
        async with lock:
            return self.device.avr.stack_pointer_read()

    async def readSREG(self):
        async with lock:
            return self.device.avr.protocol.memory_read(avr8protocol.Avr8Protocol.AVR8_MEMTYPE_OCD, 0x1C, 0x01)

    # Register and programcounter
    async def readRegs(self):
        async with lock:
            return self.device.avr.protocol.regfile_read()

    async def writeRegs(self, regs):
        async with lock:
            return self.device.avr.protocol.regile_write(regs)

    async def readProgramCounter(self):
        async with lock:
            return self.device.avr.protocol.program_counter_read()

    async def writeProgramCounter(self, programCounter):
        async with lock:
            self.device.avr.protocol.program_counter_write(programCounter)

    # SoftwareBreakpoints
    async def breakpointSWSet(self, address):
        async with lock:
            self.device.avr.protocol.software_breakpoint_set(address)
    
    async def breakpointSWClear(self, address):
        async with lock:
            self.device.avr.protocol.software_breakpoint_clear(address)

    async def breakpointSWClearAll(self):
        async with lock:
            self.device.avr.protocol.software_breakpoint_clear_all()
    
    async def breakpointHWSet(self, address):
        async with lock:
            self.device.avr.breakpoint_set(address)

    async def breakpointHWClear(self):
        async with lock:
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

