
import socket
import debugger
import signal
import sys

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 12555        # Port to listen on (non-privileged ports are > 1023)

lastPacket = ""

dbg = debugger.Debugger("atmega4809")
dbg.stop()

SIGTRAP = "S05"

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    dbg.cleanup()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

def sendPacket(socket, packetData):
    lastPacket = packetData
    checksum = sum(packetData.encode("ascii")) % 256
    message = "$" + packetData + "#" + format(checksum, '02x')
    if packetData == "":
        message = "$#00"
    print("<- " + message)
    socket.sendall(message.encode("ascii"))

def handleCommand(socket, command):
    # Required support g, G, m, M, c and s
    if "?" == command[0]:
        sendPacket(socket, SIGTRAP)
    #elif "Hc-1" in command:
        #sendPacket(socket, "OK")
    #elif "Hg-1" in command:
        #sendPacket(socket, "OK")
    #elif "qSymbol" in command:
        #sendPacket(socket, "OK")
    #elif "qAttached" in command:
        #sendPacket(socket, "0")
    #elif "qC" in command:
        #sendPacket(socket, "")
    elif "q" == command[0]:
        # Genral query
        if len(command) > 1:
            query = command[1:]
            print(query)
            if query == "Attached":
                sendPacket(socket, "0")
                return
            elif "Supported" in query:
                sendPacket(socket, "PacketSize=1000")
                return
            elif "Symbol::" in query:
                sendPacket(socket, "OK")
                return
            elif "C" == query[0]:
                sendPacket(socket, "")
                return
            elif "Offsets" in query:
                sendPacket(socket, "Text=000;Data=000;Bss=000")
                return
        sendPacket(socket, "")
    elif "s" == command[0]:
        if len(command) > 1:
            addr = command[1:]
            print(addr)
        dbg.step()
        sendPacket(socket, SIGTRAP)
    elif "c" == command[0]:
        if len(command) > 1:
            addr = command[1:]
            print(addr)
        dbg.run()
        sendPacket(socket, SIGTRAP)
    elif "m" == command[0]:
        # Assuming read from flash
        # ref https://www.nongnu.org/avr-libc/user-manual/mem_sections.html#harvard_arch
        # Memory Configuration
        # Name             Origin             Length             Attributes
        # text             0x00000000         0x0000c000         xr
        # data             0x00802800         0x00001800         rw !x
        # eeprom           0x00810000         0x00000100         rw !x
        # fuse             0x00820000         0x0000000a         rw !x
        # lock             0x00830000         0x00000400         rw !x
        # signature        0x00840000         0x00000400         rw !x
        # user_signatures  0x00850000         0x00000400         rw !x
        # *default*        0x00000000         0xffffffff
        addrSize = command[1:]
        addr = addrSize.split(",")[0]
        size = addrSize.split(",")[1]
        print(addr)
        print(size)
        addrSection = 00
        if len(addr) > 4:
            if len(addr) == 6:
                addrSection = addr[:2]
                addr = addr[2:]
            else:
                addrSection = "0" + addr[0]
                addr = addr[1:]
        
        data = bytearray()
        print(addrSection)
        if addrSection == "80":
            data = dbg.readSRAM(int(addr, 16), int(size, 16))
        elif addrSection == "81":
            data = dbg.readEEPROM(int(addr, 16), int(size, 16))
        elif addrSection == "82":
            data = dbg.readFuse(int(addr, 16), int(size, 16))
        elif addrSection == "83":
            data = dbg.readLock(int(addr, 16), int(size, 16))
        elif addrSection == "84":
            data = dbg.readSignature(int(addr, 16), int(size, 16))
        elif addrSection == "85":
            data = dbg.readUserSignature(int(addr, 16), int(size, 16))
        else:
            data = dbg.readFlash(int(addr, 16), int(size, 16))
        print(data)
        dataString = ""
        for byte in data:
            dataString = dataString + format(byte, '02x')
        print(dataString)
        sendPacket(socket, dataString)
    elif "M" == command[0]:
        # Do mem writing
        addrSizeData = command[1:]
        addr = addrSizeData.split(",")[0]
        size = (addrSizeData.split(",")[1]).split(":")[0]
        data = (addrSizeData.split(",")[1]).split(":")[1]
        print(addr)
        print(size)
        print(data)
        addrSection = 00
        if len(addr) > 4:
            if len(addr) == 6:
                addrSection = addr[:2]
                addr = addr[2:]
            else:
                addrSection = "0" + addr[0]
                addr = addr[1:]
        data = int(data, 16)
        print(data)
        data = data.to_bytes(int(size, 16), byteorder='big')
        print(data)
        print(addrSection)
        if addrSection == "80":
            data = dbg.writeSRAM(int(addr, 16), data)
        elif addrSection == "81":
            data = dbg.writeEEPROM(int(addr, 16), data)
        elif addrSection == "82":
            data = dbg.writeFuse(int(addr, 16), data)
        elif addrSection == "83":
            data = dbg.writeLock(int(addr, 16), data)
        elif addrSection == "84":
            data = dbg.writeSignature(int(addr, 16), data)
        elif addrSection == "85":
            data = dbg.writeUserSignature(int(addr, 16), data)
        else:
            # Flash write not supported here
            # EACCES
            sendPacket(socket, "E13")
        sendPacket(socket, "OK")
    elif "g" == command:
        regs = dbg.readRegs()
        sreg = dbg.readSREG()
        sp = dbg.readStackPointer()
        print([hex(no) for no in regs])
        print([hex(no) for no in sreg])
        print([hex(no) for no in sp])
        regString = ""
        for reg in regs:
            regString = regString + format(reg, '02x')
        sregString = ""
        for reg in sreg:
            sregString = sregString + format(reg, '02x')
        spString = ""
        for reg in sp:
            spString = spString + format(reg, '02x')
        regString = regString + sregString + spString
        sendPacket(socket, regString)
    elif "G" == command[0]:
        newRegData = command[1:]
        # Do reg writing
        print(newRegData)
        sendPacket(socket, "OK")
    elif "k" == command[0]:
        dbg.cleanup()
        quit()
    elif "p" == command[0]:
        # Reads register
        if len(command) > 1:
            if command[1:] == "22":
                # GDB defines PC register for AVR to be REG34(0x22)
                pc = dbg.readProgramCounter()
                print(pc)
                print(hex(pc))
                pc = pc << 1
                print(hex(pc))
                pcString = format(pc, '08x')
                print(pcString)
                pcByteAr = bytearray.fromhex(pcString.upper())
                pcByteAr.reverse()
                pcByteString = ''.join(format(x, '02x') for x in pcByteAr)
                #pcString = format(pc, '0<8x')
                # $1234abcd#54 => 0xcdab3412 in GDB
                # Preforming therefore mirror magic
                #pcStringMagicFormat = ""
                #for i in range(len(pcString)):
                #    if i % 2 == 0:
                #        if i == len(pcString)-1:
                #            pcStringMagicFormat = pcStringMagicFormat + "0" + pcString[i]
                #        else:
                #            pcStringMagicFormat = pcStringMagicFormat + pcString[i] + pcString[i+1]
                    
                #while len(pcStringMagicFormat) < 8:
                #    pcStringMagicFormat = pcStringMagicFormat + "0"
                print(pcByteString)
                sendPacket(socket, pcByteString)
    else:
        sendPacket(socket, "")

def readRegs(n):
    return "0"*2*n

def handleData(socket, data):
    if data.decode("ascii").count("$") > 0:
        for n in range(data.decode("ascii").count("$")):
            validData = True
            data = data.decode("ascii")
            #print(data)
            checksum = (data.split("#")[1])[:2]
            packet_data = (data.split("$")[1]).split("#")[0]
            if int(checksum, 16) != sum(packet_data.encode("ascii")) % 256:
                print("Checksum Wrong!")
                validData = False
            commands = []
            if validData:
                socket.sendall(b"+")
                print("<- +")
            else:
                socket.sendall(b"-")
                print("<- -")
            handleCommand(socket, packet_data)
            #for command in packet_data.split(";"):
                #handleCommand(socket, command)
                #commands.append(command.split("+")[0])
    #elif data.decode("ascii").count("-") > 0:
        #sendPacket(socket, lastPacket)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            # Should iterate through buffer and take out commands/escape characters
            data = conn.recv(1024)
            if len(data) > 0:
                print("-> " + data.decode('ascii'))
                handleData(conn, data)

