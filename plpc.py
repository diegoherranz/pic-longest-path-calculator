# PLPC
# PIC LONGEST PATH CALCULATOR

# Copyright (C) 2011 Diego Herranz

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import time
import subprocess
import tempfile
from optparse import OptionParser

def printverbose(toPrint, depth=0):
	"""Prints only if verbose is enabled. Adds as many tabs as depth parameter"""
	if options.verbose:
		print ('\t'*depth+toPrint)

#Instructions
#instruction:[size (bytes), cycles (no exec. change in conditionals), conditional?, typeOfInstruction]
instructions={
	"addwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"addwfc":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"andwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"clrf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"comf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"cpfseq":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"cpfsgt":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"cpfslt":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"decf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"decfsz":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"dcfsnz":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"incf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"incfsz":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"infsnz":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"iorwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"movf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"movff":{"size":4, "cycles":2, "conditional":False, "type":"Normal"},
	"movwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"mulwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"negf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"rlcf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"rlncf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"rrcf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"rrncf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"setf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"subfwb":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"subwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"subwfb":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"swapf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"tstfsz":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"xorwf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"bcf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"bsf":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"btfsc":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"btfss":{"size":2, "cycles":1, "conditional":True, "type":"Skip"},
	"btg":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"bc":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bn":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bnc":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bnn":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bnov":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bnz":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bov":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"bra":{"size":2, "cycles":2, "conditional":False, "type":"Branch"},
	"bz":{"size":2, "cycles":1, "conditional":True, "type":"Branch"},
	"call":{"size":4, "cycles":2, "conditional":False, "type":"Call"},
	"clrwdt":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"daw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"goto":{"size":4, "cycles":2, "conditional":False, "type":"Branch"},
	"nop":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"pop":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"push":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"rcall":{"size":2, "cycles":2, "conditional":False, "type":"Call"},
	"reset":{"size":2, "cycles":1, "conditional":False, "type":"Unknown"},
	"retfie":{"size":2, "cycles":2, "conditional":False, "type":"Return"},
	"retlw":{"size":2, "cycles":2, "conditional":False, "type":"Return"},
	"return":{"size":2, "cycles":2, "conditional":False, "type":"Return"},
	"sleep":{"size":2, "cycles":1, "conditional":False, "type":"Unknown"},
	"addlw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"andlw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"iorlw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"lfsr":{"size":4, "cycles":2, "conditional":False, "type":"Normal"},
	"movlb":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"movlw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"mullw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"sublw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"xorlw":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"blrd*":{"size":2, "cycles":1, "conditional":False, "type":"Normal"},
	"tblrd":{"size":2, "cycles":2, "conditional":False, "type":"Normal"},
	"tblwt":{"size":2, "cycles":2, "conditional":False, "type":"Normal"},
	"unknown":{"size":2, "cycles":1, "conditional":False, "type":"Unknown"}
}




programMemory={}

#disassembler line examples
#000674:  2ae1  incf	0xe1, 0x1, 0
#000676:  ec02  call	0x4, 0
#000678:  f000
#00067a:  d012  bra	0x6a0
#00067c:  c088  movff	0x88, 0x85

def instructionInDisassemblerLine(disassemblerLine):

	try:
		instruction=disassemblerLine.split()[2]
		if instruction in instructions.keys():
			return instruction
	except:	
		# If not instruction found, if migth be a nop if instruction is 0xfnnn (address 000678 in the example lines before)
		if disassemblerLine.split()[1][0] == 'f':
			return "nop"	
		
	return "unknown"
	

def addressInDisassemblerLine(disassemblerLine):

	return int(disassemblerLine.partition(':')[0], 16)

def addressArgumentInDisassemblerLine(disassemblerLine):
	
	#There's a '\t' between instruction (i.e. movff) and argument (i.e 0x88, 0x85)
	arguments=disassemblerLine.partition('\t')[2]

	try:
		addressArgument=int(arguments.partition(',')[0], 16)
	except:
		addressArgument=0
			
	return addressArgument



def processHEX(hexfile):
	"""Calls gpdasm disassembler and..."""

	f = tempfile.TemporaryFile(mode='w+t')
	args=["gpdasm", "-p"+options.processor, hexfile]
	p=subprocess.Popen(args, stdout=f)
	printverbose("Disassembler call: "+" ".join(args)+"\n")
	p.wait()

	f.seek(0)

	for line in f:

		address=addressInDisassemblerLine(line)
		instruction=instructionInDisassemblerLine(line)
		if instructions[instruction]["type"] == "Call" or instructions[instruction]["type"] == "Branch":
			addressArgument=addressArgumentInDisassemblerLine(line)
		else:
			addressArgument=''

		programMemory[address]=[instruction, addressArgument]

	f.close()


def maxCycles(pc, stack, depth):	
	"""Returns the maximum number of cycles starting at pc until a RETURN, RETLW or RETFIE is found."""

	endReached=False
	cycles=0

	while(not endReached):
		printverbose (str(cycles)+" cycles since last conditional", depth=depth)
		printverbose ("Next PC="+hex(pc)+"\n", depth=depth)
		time.sleep(options.delay)
		instruction=programMemory[pc][0]
		addressArgument=programMemory[pc][1]

		if addressArgument == '':
			printverbose ("PC="+hex(pc)+": "+instruction+" ("+str(instructions[instruction]["cycles"])+" cycles)", depth)
		else:
			printverbose ("PC="+hex(pc)+": "+instruction+' '+hex(addressArgument)+" ("+str(instructions[instruction]["cycles"])+" cycles)", depth)
			
		if instructions[instruction]["type"] == "Unknown":
			print (instruction+" instruction found at address "+hex(pc)+". Can't continue.")
			exit(1)

		if not instructions[instruction]["conditional"]:			
			printverbose ('\t'+"Unconditional instruction", depth)
			cycles += instructions[instruction]["cycles"]
			pc += instructions[instruction]["size"]

			if instructions[instruction]["type"] == "Call":
				stack.append(pc)
				printverbose ('\t'+hex(pc)+" pushed to stack", depth)

			if instructions[instruction]["type"] == "Branch" or instructions[instruction]["type"] == "Call":
				pc = addressArgument

			if instructions[instruction]["type"] == "Return":
				try:
					pc=stack.pop()
					printverbose ('\t'+hex(pc)+" poped from stack", depth)	
				except:
					endReached = True
					printverbose ('\t'+"Stack underflow. End reached", depth)
					
			printverbose (" ")
		
		if instructions[instruction]["conditional"]:
			printverbose ('\t'+"Conditional instruction\n", depth)

			endReached = True

			cycles += instructions[instruction]["cycles"]
			pc += instructions[instruction]["size"]


			if instructions[instruction]["type"] == "Skip":
				printverbose ("PATH 1 (no skip)", depth=depth+1)				
				cyclesPath1=maxCycles(pc, stack[:], depth=depth+1) #Execution unchanged			

				printverbose ("PATH 2 (skip) (+1 cycle)", depth=depth+1)				
				cyclesPath2=maxCycles(pc+2, stack[:], depth=depth+1) #Execution changed (Inst skipped)

				cycles+=max(cyclesPath1, cyclesPath2+1)

			if instructions[instruction]["type"] == "Branch":
				printverbose ("PATH 1 (no branch)", depth=depth+1)				
				cyclesPath1=maxCycles(pc, stack[:], depth=depth+1) #Execution unchanged				

				printverbose ("PATH 2 (branch) (+1 cycle)", depth=depth+1)				
				cyclesPath2=maxCycles(addressArgument, stack[:], depth=depth+1) #Execution changed (branch)

				cycles+=max(cyclesPath1, cyclesPath2+1)		
				
		
		
		

	return cycles

options = ''

def main():
	global options		
	usage = "usage: python %prog [options] hexfile"
	parser = OptionParser(usage=usage)
	parser.add_option("-p", "--processor", dest="processor", help="processor model (default=%default)", metavar="PROC", default="18f2550")
	parser.add_option("-s", "--start", type="int", dest="startAddress",help="start address (default=0x%default). Decimal or hexadecimal (0xnnn) formats accepted", metavar="START_ADDRESS", default=0x08)
	parser.add_option("-f", "--frequency", type="float", dest="frequency",help="osc. frequency (default=8MHz). Scientific notation accepted, i.e. 4.2e6 (4.2 MHz)", metavar="FREQ", default=8.0e6)
	parser.add_option("-d", "--delay", type="float", dest="delay",help="delay time in seconds between instructions (default=%default sec). Useful with verbose to follow execution", metavar="TIME", default=0)
	parser.add_option("-v", "--verbose",action="store_true", dest="verbose", default=False,help="trace execution with useful info")
	(options, args) = parser.parse_args()
	try:
		hexfile=args[0]
	except:
		parser.print_help()
		sys.exit(2)



	processHEX(hexfile)
	printverbose ("\n**** STARTING CALCULATIONS ****")
	cycles=maxCycles(pc=options.startAddress, stack=[], depth=0)

	printverbose ("\n**** FINAL RESULT ****")
	print "Longest Path="+str(cycles)+" cycles"
	print "Execution time="+format(4.0*cycles/options.frequency, 'g')+" sec. @ "+format(options.frequency, "g")+" Hz"


if __name__ == "__main__":
	main()
