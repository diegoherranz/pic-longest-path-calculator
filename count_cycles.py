## COUNT CYCLES

## Diego Herranz 2011

import sys
import time
import subprocess
from optparse import OptionParser
import tempfile
from copy import copy

ids=set([])

#Instructions
#instruction:[size (bytes), cycles (conditionals if no exec change), conditional?, typeOfInstruction]
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
	"reset":[2, 1, "Unconditional", "No idea"],
	"retfie":[2, 2, "Unconditional", "Return"],
	"retlw":[2, 2, "Unconditional", "Return"],
	"return":[2, 2, "Unconditional", "Return"],
	"sleep":[2, 1, "Unconditional", "No idea"],
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
	"tblrd*+":[2, 1, "Unconditional", "Normal"],
	"tblrd*-":[2, 1, "Unconditional", "Normal"],
	"tblrd+*":[2, 1, "Unconditional", "Normal"],
	"tblwt*":[2, 1, "Unconditional", "Normal"],
	"tblwt*+":[2, 1, "Unconditional", "Normal"],
	"tblwt*-":[2, 1, "Unconditional", "Normal"],
	"tblwt+*":[2, 1, "Unconditional", "Normal"],
	"unknown":[2, 1, "Unconditional", "Normal"]
}

memory={}

def printif(toPrint):
	if options.verbose:
		print toPrint

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


#line example
#0008d0:  cffa  movff	0xffa, 0xfe5

def instructionInInstructionLine(instructionLine):

	for instruction in instructions.keys():
		if instructionLine.count(instruction+'\t') > 0 or instructionLine.count(instruction+'\n') > 0:
			return instruction
	return "unknown"

def addressInInstructionLine(instructionLine):

	return int(instructionLine.partition(':')[0], 16)

def importantArgumentInInstructionLine(instructionLine):
	
	arguments=instructionLine.partition('\t')[2]

	try:
		importantArgument=int(arguments.partition(',')[0], 16)
	except:
		importantArgument=0
			
	return importantArgument



def processHEX(hexfile):
	"""Calls gpdasm disassembler and..."""

	f = tempfile.TemporaryFile(mode='w+t')
	args=["gpdasm", "-p"+options.processor, hexfile]
	p=subprocess.Popen(args, stdout=f)
	printif("Disassembler call:"+" ".join(args))
	p.wait()

	f.seek(0)

	for line in f:

		address=addressInInstructionLine(line)
		instruction=instructionInInstructionLine(line)
		if instructionType(instruction) == "Call" or instructionType(instruction) == "Branch":
			importantArgument=importantArgumentInInstructionLine(line)
		else:
			importantArgument=''

		memory[address]=[instruction, importantArgument]

		

		#print line.rstrip('\n')
		#print memory[address]	
	
	f.close()


def maxCyclesStartingAt(pc, stack):
	
	conditionalInstructionFound=False
	endReached=False
	cycles=0

	while((not conditionalInstructionFound) and (not endReached)):
		instruction=memory[pc][0]
		importantArgument=memory[pc][1]

		if importantArgument == '':
			printif ("\nPC="+hex(pc)+": "+instruction)
		else:
			printif ("\nPC="+hex(pc)+": "+instruction+' '+hex(importantArgument))

		if(not isInstructionConditional(instruction)):			
			printif ('\t'+"Unconditional instruction")
			cycles+=instructionCycles(instruction)
			pc+=instructionSize(instruction)

			if instructionType(instruction)=="Call":
				stack.append(pc)

			if instructionType(instruction)=="Branch" or instructionType(instruction)=="Call":
				pc=importantArgument

			if instructionType(instruction)=="Return":
				try:
					pc=stack.pop()	
				except:
					endReached = True
		
		if(isInstructionConditional(instruction)):
			printif ('\t'+"Conditional instruction")

			conditionalInstructionFound = True

			cycles+=instructionCycles(instruction)
			pc+=instructionSize(instruction)

			stackSize=len(stack)

			if instructionType(instruction)=="Skip":
				printif ("PATH 1 (no skip)")
				stackLast=stack[:]
				cyclesPath1=maxCyclesStartingAt(pc, stack[:]) #Execution unchanged

				if stack != stackLast:
					print "Stack has been modified"
					exit(1)

				printif ("PATH 2 (skip)")
				stackLast=stack[:]
				cyclesPath2=maxCyclesStartingAt(pc+2, stack[:]) #Execution changed (Inst skipped)

				if stack != stackLast:
					print "Stack has been modified"
					exit(1)

				cycles+=max(cyclesPath1, cyclesPath2+1)

			if instructionType(instruction)=="Branch":
				printif ("PATH 1 (no branch)")
				stackLast=stack[:]
				cyclesPath1=maxCyclesStartingAt(pc, stack[:]) #Execution unchanged

				if stack != stackLast:
					print "Stack has been modified"
					exit(1)

				printif ("PATH 2 (branch)")
				stackLast=stack[:]
				cyclesPath2=maxCyclesStartingAt(importantArgument, stack[:]) #Execution changed (branch)

				if stack != stackLast:
					print "Stack has been modified"
					exit(1)

				cycles+=max(cyclesPath1, cyclesPath2+1)

			
			
			
			
		printif ('\t'+"Next PC="+hex(pc))
		printif ('\t'+"Cycles after this instruction="+str(cycles))
		time.sleep(options.sleepTime)

	return cycles



	
usage = "usage: python %prog [options] hexfile"
parser = OptionParser(usage=usage)
parser.add_option("-p", "--processor", dest="processor", help="processor model (default=%default).", metavar="PROC", default="18f2550")
parser.add_option("-a", "--address", type="int", dest="startAddress",help="start address (default=0x%default). Decimal or hexadecimal (0xnnn) formats accepted.", metavar="START_ADDRESS", default=0x08)
parser.add_option("-f", "--frequency", type="float", dest="frequency",help="osc. frequency (default=8MHz). Scientific notation accepted, i.e. 4.2e6 (4.2 MHz)", metavar="FREQ", default=8.0e6)
parser.add_option("-s", "--sleep", type="float", dest="sleepTime",help="sleep time in seconds after each instruction (default=%default sec). Useful with verbose to follow execution.", metavar="TIME", default=0)
parser.add_option("-v", "--verbose",action="store_true", dest="verbose", default=False,help="print status messages to stdout")
(options, args) = parser.parse_args()
try:
	hexfile=args[0]
except:
	parser.print_help()
	sys.exit(2)





processHEX(hexfile)
cycles=maxCyclesStartingAt(pc=options.startAddress, stack=[])

print "\n**** FINAL RESULT ****"
print "Longest Path="+str(cycles)+" cycles"
print "Execution time="+format(4.0*cycles/options.frequency, 'g')+" sec. @ "+format(options.frequency, "g")+" Hz\n"




