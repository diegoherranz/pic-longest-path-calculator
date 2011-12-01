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
	"addwf":[2, 1, "Unconditional", "Normal"],
	"addwfc":[2, 1, "Unconditional", "Normal"],
	"andwf":[2, 1, "Unconditional", "Normal"],
	"clrf":[2, 1, "Unconditional", "Normal"],
	"comf":[2, 1, "Unconditional", "Normal"],
	"cpfseq":[2, 1, "Conditional", "Skip"],
	"cpfsgt":[2, 1, "Conditional", "Skip"],
	"cpfslt":[2, 1, "Conditional", "Skip"],
	"decf":[2, 1, "Unconditional", "Normal"],
	"decfsz":[2, 1, "Conditional", "Skip"],
	"dcfsnz":[2, 1, "Conditional", "Skip"],
	"incf":[2, 1, "Unconditional", "Normal"],
	"incfsz":[2, 1, "Conditional", "Skip"],
	"infsnz":[2, 1, "Conditional", "Skip"],
	"iorwf":[2, 1, "Unconditional", "Normal"],
	"movf":[2, 1, "Unconditional", "Normal"],
	"movff":[4, 2, "Unconditional", "Normal"],
	"movwf":[2, 1, "Unconditional", "Normal"],
	"mulwf":[2, 1, "Unconditional", "Normal"],
	"negf":[2, 1, "Unconditional", "Normal"],
	"rlcf":[2, 1, "Unconditional", "Normal"],
	"rlncf":[2, 1, "Unconditional", "Normal"],
	"rrcf":[2, 1, "Unconditional", "Normal"],
	"rrncf":[2, 1, "Unconditional", "Normal"],
	"setf":[2, 1, "Unconditional", "Normal"],
	"subfwb":[2, 1, "Unconditional", "Normal"],
	"subwf":[2, 1, "Unconditional", "Normal"],
	"subwfb":[2, 1, "Unconditional", "Normal"],
	"swapf":[2, 1, "Unconditional", "Normal"],
	"tstfsz":[2, 1, "Conditional", "Skip"],
	"xorwf":[2, 1, "Unconditional", "Normal"],
	"bcf":[2, 1, "Unconditional", "Normal"],
	"bsf":[2, 1, "Unconditional", "Normal"],
	"btfsc":[2, 1, "Conditional", "Skip"],
	"btfss":[2, 1, "Conditional", "Skip"],
	"btg":[2, 1, "Unconditional", "Normal"],
	"bc":[2, 1, "Conditional", "Branch"],
	"bn":[2, 1, "Conditional", "Branch"],
	"bnc":[2, 1, "Conditional", "Branch"],
	"bnn":[2, 1, "Conditional", "Branch"],
	"bnov":[2, 1, "Conditional", "Branch"],
	"bnz":[2, 1, "Conditional", "Branch"],
	"bov":[2, 1, "Conditional", "Branch"],
	"bra":[2, 2, "Unconditional", "Branch"],
	"bz":[2, 1, "Conditional", "Branch"],
	"call":[4, 2, "Unconditional", "Call"],
	"clrwdt":[2, 1, "Unconditional", "Normal"],
	"daw":[2, 1, "Unconditional", "Normal"],
	"goto":[4, 2, "Unconditional", "Branch"],
	"nop":[2, 1, "Unconditional", "Normal"],
	"pop":[2, 1, "Unconditional", "Normal"],
	"push":[2, 1, "Unconditional", "Normal"],
	"rcall":[2, 2, "Unconditional", "Call"],
	"reset":[2, 1, "Unconditional", "Unknown"],
	"retfie":[2, 2, "Unconditional", "Return"],
	"retlw":[2, 2, "Unconditional", "Return"],
	"return":[2, 2, "Unconditional", "Return"],
	"sleep":[2, 1, "Unconditional", "Unknown"],
	"addlw":[2, 1, "Unconditional", "Normal"],
	"andlw":[2, 1, "Unconditional", "Normal"],
	"iorlw":[2, 1, "Unconditional", "Normal"],
	"lfsr":[4, 2, "Unconditional", "Normal"],
	"movlb":[2, 1, "Unconditional", "Normal"],
	"movlw":[2, 1, "Unconditional", "Normal"],
	"mullw":[2, 1, "Unconditional", "Normal"],
	"sublw":[2, 1, "Unconditional", "Normal"],
	"xorlw":[2, 1, "Unconditional", "Normal"],
	"blrd*":[2, 1, "Unconditional", "Normal"],
	"tblrd":[2, 2, "Unconditional", "Normal"],
	"tblwt":[2, 2, "Unconditional", "Normal"],
	"unknown":[2, 1, "Unconditional", "Unknown"]
}

def instructionSize(instruction):
	return instructions[instruction][0]

def instructionCycles(instruction):
	return instructions[instruction][1]

def isInstructionConditional(instruction):
	if instructions[instruction][2] == "Conditional":
		return True
	else:
		return False

def instructionType(instruction):
	return instructions[instruction][3]


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
		if instructionType(instruction) == "Call" or instructionType(instruction) == "Branch":
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
			printverbose ("PC="+hex(pc)+": "+instruction+" ("+str(instructionCycles(instruction))+" cycles)", depth)
		else:
			printverbose ("PC="+hex(pc)+": "+instruction+' '+hex(addressArgument)+" ("+str(instructionCycles(instruction))+" cycles)", depth)
			
		if instructionType(instruction)=="Unknown":
			print (instruction+" instruction found at address "+hex(pc)+". Can't continue.")
			exit(1)

		if(not isInstructionConditional(instruction)):			
			printverbose ('\t'+"Unconditional instruction", depth)
			cycles+=instructionCycles(instruction)
			pc+=instructionSize(instruction)

			if instructionType(instruction)=="Call":
				stack.append(pc)
				printverbose ('\t'+hex(pc)+" pushed to stack", depth)

			if instructionType(instruction)=="Branch" or instructionType(instruction)=="Call":
				pc=addressArgument

			if instructionType(instruction)=="Return":
				try:
					pc=stack.pop()
					printverbose ('\t'+hex(pc)+" poped from stack", depth)	
				except:
					endReached = True
					printverbose ('\t'+"Stack underflow. End reached", depth)
					
			printverbose (" ")
		
		if(isInstructionConditional(instruction)):
			printverbose ('\t'+"Conditional instruction\n", depth)

			endReached = True

			cycles+=instructionCycles(instruction)
			pc+=instructionSize(instruction)


			if instructionType(instruction)=="Skip":
				printverbose ("PATH 1 (no skip)", depth=depth+1)				
				cyclesPath1=maxCycles(pc, stack[:], depth=depth+1) #Execution unchanged			

				printverbose ("PATH 2 (skip) (+1 cycle)", depth=depth+1)				
				cyclesPath2=maxCycles(pc+2, stack[:], depth=depth+1) #Execution changed (Inst skipped)

				cycles+=max(cyclesPath1, cyclesPath2+1)

			if instructionType(instruction)=="Branch":
				printverbose ("PATH 1 (no branch)", depth=depth+1)				
				cyclesPath1=maxCycles(pc, stack[:], depth=depth+1) #Execution unchanged				

				printverbose ("PATH 2 (branch) (+1 cycle)", depth=depth+1)				
				cyclesPath2=maxCycles(addressArgument, stack[:], depth=depth+1) #Execution changed (branch)

				cycles+=max(cyclesPath1, cyclesPath2+1)		
				
		
		
		

	return cycles


##MAIN	
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
