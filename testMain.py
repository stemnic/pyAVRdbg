import debugger
import logging

dbg = debugger.Debugger("atmega4809")
dbg.stop()
#logging.info(dbg.readRegs())
#logging.info(dbg.readSRAM(0x00, 1024))
#logging.info(dbg.readSREG())
#logging.info(dbg.readStackPointer())
dbg.pollEvent()
dbg.run()
dbg.pollEvent()
dbg.pollEvent()
#logging.info(dbg.readRegs())

dbg.cleanup()