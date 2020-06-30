import debugger
import logging

dbg = debugger.Debugger("atmega4809")
dbg.stop()
logging.info(dbg.readRegs())
logging.info(dbg.readMemory(0x00, 1024))
dbg.run()

dbg.cleanup()