PIC Longest Path Calculator
=======================

Introduction
---------------

*PIC Longest Path Calculator (PLPC)* is a Python tool to calculate the maximum number of cycles required to execute a PIC function reading a hex file. It also shows the maximum execution time at a specified frequency from the number of cycles calculated before.
  
Execution starts at specified address and ends when a RETURN, RETLW or RETFIE instruction is found\footnote{It has to be a RETURN, RETLW or RETFIE with empty call stack so if a call is made, the return instruction in that rutine doesn't make \productstring{} end.}.



Examples
--------

Starting at address 0x08 (high priority interrupt), frequency 8 MHz:

	$ python plpc.py hexfile.hex

	Longest Path=46 cycles
	Execution time=2.3e-05 sec. @ 8e+06 Hz

Starting at address 0x08 (high priority interrupt), frequency 8 MHz, verbose and 2 seconds delay between instructions.

	$ python plpc.py -v -d 2 hexfile.hex

	[...] Verbose execution of the program

	Longest Path=46 cycles
	Execution time=2.3e-05 sec. @ 8e+06 Hz
	
Starting at address 0x7b4, frequency 2 MHz.

	$ python plpc.py -s 0x7b4 -f 2e6 hexfile.hex

	Longest Path=3 cycles
	Execution time=6e-06 sec. @ 2e+06 Hz





Known limitations and workarounds
---------------------------------------------

### Loops
You can notice [...] if python says "maximum recursion depth exceeded".

* Undefined loops
		
		while(PORTBbits.PORTB1){
		[...]
		}			

__Problem__: There is no way to know when that loop is going to end. So \productstring{} always consideres the posibility of remaining inside the loop. 

__Workaround__:

* Defined loops

__Problem__:

__Workaround__:


### Jump tables or writings to PC
		
__Problem__: Jump tables can be created by writing program counter (PC) directly. This changes the execution path, but whereas a call, bra, conditional bra, or similar instructions include an argument specifying the next address to be executed, writing to PC would require a simulator to know the following address to be executed.
			
SDCC uses jump tables for switch statements (please let me know if jump tables are used anywhere else).			
	
__Problem__: Rewriting *switch* statements as several *if* statements could solve the problem although it creates the possibility of a path longer than the actual longest. This is because in a *switch* only one path is executed\footnote{If using break sentences.} and using several *if*, \productstring{} will consider the possibility of every *if* being executed, which wouldn't happen actually.


Support, bugs or contact
------------------------
If find any bug or have an improvement don't hesitate to contact, fork or pull request.
