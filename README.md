# pyAVRdbg
An attempt of making a gdb rsp server for AVR debuggers with [pymcuprog](https://pypi.org/project/pymcuprog/) primarily for the new UPDI devices but other protocols supported by pymcuprog can easily be made to work.

## Current Features
- Stepping
- Memory manipulation (viewing and modifying variables)
- Hardware and software breakpoints
- Reading Registers (including SREG, Stack pointer and program counter)*

*Writing is possible it is just not implemented yet.

## Install/Dependencies

- avr-gdb
    - Recommend using the latest version. If you are compiling it I would looking at the arch community repos [buildfile](https://git.archlinux.org/svntogit/community.git/tree/trunk/PKGBUILD?h=packages/avr-gdb)
    - Windows users might want to use wsl
- libusb might be required as a seperate install
- pip3 install --user pymcuprog
    - Some form for C++ compiler if you are running python versions higher than 3.6 since pymcuprog needs to compile package with Cython
        - Windows:
            - VC++ 2015.3 v14.00 (v140) installed through [Visual Studio](https://visualstudio.microsoft.com/downloads/)

## Usage

### Debugger server
1. Ensure debugger/kit is connected
2. Modify main.py with device name see [supported devices](#currently-supported-devices) and ip or port defines if applicable
3. start main.py

### GDB
1. `avr-gdb (wellNamed).elf`
2. (gdb) `target remote IP:Port`

## Currently Supported Devices
These are all the currently supported devices per 03.06.2020. This list is wholly dependent on pymcuprog's device support since this RSP server only uses general library calls in pymcuprog. As mentioned before ISP devices might also be supported in the future.
| Protocol | Device Name |
|:--------:|:-----------:|
| UPDI     | atmega4808*  |
|          | atmega4809 |
|          | attiny416*  |
|          | attiny817*  |
|          |attiny1607*|
|          |attiny1627*|
|          |attiny3217*|
|          |avr128da28*|
|          |avr128da48|
|          |avr128db48*|

*Devices are untested but will most likely work.

## Thanks
A huge thanks to Microchip for making pymcuprog available 

## Some useful links for referance for development
- https://www.embecosm.com/appnotes/ean4/embecosm-howto-rsp-server-ean4-issue-2.html#id3033520
- https://ftp.gnu.org/old-gnu/Manuals/gdb/html_node/gdb_toc.html
- https://onlinedocs.microchip.com/pr/GUID-33422CDF-8B41-417C-9C31-E4521ADAE9B4-en-US-2/index.html
- https://github.com/mbedmicro/pyOCD/tree/master/pyocd
- https://developer.apple.com/library/archive/documentation/DeveloperTools/gdb/gdb/gdb_33.html