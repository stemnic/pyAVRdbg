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

logging.basicConfig(level=logging.DEBUG,handlers=[logging.StreamHandler()])

lock = asyncio.Lock()

#def pollingThread(eventReciver: AvrCommand):
#    reciver = eventReciver
#    while True:
##            logging.info(reciver.poll_events())

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
        #threading.Thread(target=pollingThread, args=(self.eventReciver,)).start()
    
    def pollEvent(self):
        eventRegister = self.eventReciver.poll_events()
        for byte in eventRegister:
            print(hex(byte), end=' ')
        logging.info(eventRegister)
        if eventRegister[0] == AvrCommand.AVR_EVENT: # Verifying data is an event
            size = int.from_bytes(eventRegister[1:3], byteorder='big')
            if size != 0:
                #event recived
                logging.info("Event recived")
                eventarray = eventRegister[3:(size+1+3)]
                logging.info(eventarray)
                return eventarray
            else:
                logging.info("No event")
                return None

    # Memory interaction
    def writeSRAM(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('internal_sram'))['address']
        return self.device.write(self.memoryinfo.memory_info_by_name('internal_sram'), address-offset, data)

    def readSRAM(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('internal_sram'))['address']
        return self.device.read(self.memoryinfo.memory_info_by_name('internal_sram'), address-offset, numBytes)

    def readFlash(self, address, numBytes):
        return self.device.read(self.memoryinfo.memory_info_by_name('flash'), address, numBytes)

    def writeEEPROM(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('eeprom'))['address']
        return self.device.write(self.memoryinfo.memory_info_by_name('eeprom'), address-offset, data)

    def readEEPROM(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('eeprom'))['address']
        return self.device.read(self.memoryinfo.memory_info_by_name('eeprom'), address-offset, numBytes)

    def writeFuse(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('fuses'))['address']
        return self.device.write(self.memoryinfo.memory_info_by_name('fuses'), address-offset, data)

    def readFuse(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('fuses'))['address']
        return self.device.read(self.memoryinfo.memory_info_by_name('fuses'), address-offset, numBytes)

    def writeLock(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('lockbits'))['address']
        return self.device.write(self.memoryinfo.memory_info_by_name('lockbits'), address-offset, data)

    def readLock(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('lockbits'))['address']
        return self.device.read(self.memoryinfo.memory_info_by_name('lockbits'), address-offset, numBytes)

    def writeSignature(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('signatures'))['address']
        return self.device.write(self.memoryinfo.memory_info_by_name('signatures'), address-offset, data)

    def readSignature(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('signatures'))['address']
        return self.device.read(self.memoryinfo.memory_info_by_name('signatures'), address-offset, numBytes)

    def writeUserSignature(self, address, data):
        offset = (self.memoryinfo.memory_info_by_name('user_row'))['address']
        return self.device.write(self.memoryinfo.memory_info_by_name('user_row'), address-offset, data)

    def readUserSignature(self, address, numBytes):
        offset = (self.memoryinfo.memory_info_by_name('user_row'))['address']
        return self.device.read(self.memoryinfo.memory_info_by_name('user_row'), address-offset, numBytes)

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

    def readStackPointer(self):
        return self.device.avr.stack_pointer_read()

    def readSREG(self):
        return self.device.avr.protocol.memory_read(avr8protocol.Avr8Protocol.AVR8_MEMTYPE_OCD, 0x1C, 0x01)

    # Register and programcounter
    def readRegs(self):
        return self.device.avr.protocol.regfile_read()

    def writeRegs(self, regs):
        return self.device.avr.protocol.regile_write(regs)

    def readProgramCounter(self):
        return self.device.avr.protocol.program_counter_read()

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

