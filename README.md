PIC Longest Path Calculator
=======================

[![Build Status](https://travis-ci.org/diegoherranz/pic-longest-path-calculator.svg?branch=master)](https://travis-ci.org/diegoherranz/pic-longest-path-calculator)


Introduction
------------

*PIC Longest Path Calculator (PLPC)* is a Python tool to calculate the maximum number of cycles (or execution time at a given frequency) required to execute a PIC18 (16-bit instruction bus) function. It's useful for critical or real-time systems which need to know the worst-case maximum execution time of a routine. For example, to know if a periodic interrupt will always be able to run before the next period and to get an idea of CPU computing time available for other tasks.

The input file used is directly the HEX file that would be "flashed" on the PIC.


Requirements
------------
- Python 2.7
- [gputils](http://gputils.sourceforge.net/). Installation instructions [here](https://github.com/diegoherranz/sdcc-examples#gputils-installation-only-for-pic-ports).


Operating principle
-------------------
Execution starts at specified address of the PIC program memory and ends when a return-like instruction (`RETURN`, `RETLW` or `RETFIE`) is found on the same level, i.e. if another function is called, the return from that function does not make PLPC end.

Whenever a conditional instruction is found (e.g. `BTFSC`, `BZ`, etc.), both possible paths are analyzed. On each of those possibilities, a conditional instruction will again open two possible paths and so on recursively. Thus, execution path opens like a tree. Finally, the longest path on the tree will be the longest execution path or worst case.

Due to the use of recursion, the code is quite simple and easy to read.


Examples
--------

 - Starting at address 0x08 (high priority interrupt), frequency 8 MHz:

        $ python plpc.py hexfile.hex

        Longest Path = 46 cycles
        Execution time = 2.3e-05 sec. @ 8e+06 Hz

 - Starting at address 0x08 (high priority interrupt), frequency 8 MHz, verbose and 2 seconds delay between instructions.

        $ python plpc.py -v -d 2 hexfile.hex

        [...] Verbose execution of the program showing cycles, jumps, conditional instructions, etc.

        Longest Path = 46 cycles
        Execution time = 2.3e-05 sec. @ 8e+06 Hz

- Starting at a function which is located at address 0x7b4, frequency 2 MHz.

        $ python plpc.py -s 0x7b4 -f 2e6 hexfile.hex

        Longest Path = 3 cycles
        Execution time = 6e-06 sec. @ 2e+06 Hz


Known limitations and workarounds
---------------------------------

### Loops
You can notice there is a problem with a loop if python complains with "maximum recursion depth exceeded". This can happen with diferent types of loops:

- **Undefined loops**. There are loops which depend on something external like this one:

		while(PORTBbits.PORTB1){
		[...]
		}		
There is no way to know when that loop is going to end. So PLPC always considers the posibility of remaining inside the loop. Workaround: remove the loop or replace it with several non conditional instructions.

- **Defined loops**. Even if the loop has a defined number of cycles after which it will always exit, a full simulator would be needed. Workaround: none.

### Jump tables or writings to PC

Jump tables can be created by writing program counter (PC) directly. This changes the execution path, but whereas a `CALL`, `BRA`, `BZ` or similar instructions include an argument specifying the next address to be executed, writing to PC would require a full simulator to know the following address to be executed.

For instance, [SDCC](http://sdcc.sourceforge.net/) uses jump tables for switch statements.

Workaround: Rewriting *switch* statements as several *if* statements could solve the problem although it creates a path with may have a slightly different length.


gpsim integration
-----------------
As seen previously, the fact of not being a full PIC simulator makes very hard to analyze the maximum execution path on many cases. It would be interesting to integrate this idea in a full simulator like [gpsim](http://gpsim.sourceforge.net/) which should be easier than extending PLPC to be a full simulator.


Support, bugs or contact
------------------------
If find any bug or have an improvement don't hesitate to open an issue or fork and pull request.
