from memory import *
from processor import *
from assembler import *


class LinkableAssembler(object):
	def __init__(self,processor,fname,startname,debug=0,*args):
		self.processor=processor
		prepr=Preprocessor(fname)
		prepr.do_all()
		# use the preprocessed file.
		self.f=open(fname+".pr","r")
		self.lines=self.f.read().split("\n")
		f.close()
		os.system("rm -f "+fname+"\.pr*")
		self.compiled={}
		self.debug=debug
		self.lineno=0
		self.blockno=0

		# from assembler.Assembler
		# symbolic names are dereferenced by the assembler
		self.support_symbolic_names=["jmp","call","jne","jeq","jle","jge","jlt","jgt"]
		self.support_static_symbolic_names=["mov","ldi"]
		self.i_commands=["ldi","addi","subi","xori","ori","andi","modi"]
		# XXX NEW: some mnemonics support only register indices !
		self.register_only=["add","sub","mul","div","mod","and","or","xor","neg","inc","dec"]

		# now the address space:
		# highest register index
		self.register_hi=self.ram.

		self.commands={v:k for k,v in self.processor.tb_commands.items()}
		self.commands.update({v:k for k,v in self.processor.db_commands.items()})
		self.commands.update({v:k for k,v in self.processor.sg_commands.items()})
		self.tb_commands={v:k for k,v in self.processor.tb_commands.items()}
		self.db_commands={v:k for k,v in self.processor.db_commands.items()}
		self.sg_commands={v:k for k,v in self.processor.sg_commands.items()}
		self.current_object="start"
	def compile(self):
		""" compiling as relocatable is a bit more difficult.
			We need to save a lot more data to do this.
			So the layout is as following:
			{(startname,objectname,blockno):block}
			this allows rearranging of blocks by a linker. """
		for line in self.lines:
			# as usual: move through all lines
			if(self.debug>0):
				print("compiling lineno {0}, blockno {1} : '{2}'".format(self.lineno,self.blockno,line))
			cms=line.split()
			if(len(cms)==0):
				if(self.debug>4):
					print("skipping line '{0}' (is empty)".format(line))
				continue
			# supporting characters
			# also from assembler.Assembler
			if(len(cms)>=2 and cms[1][0]=="'"):
				cms[1]=hex(ord(cms[1][1:-1]))[2:] # as we are using still strings ;-)
			if(len(cms)>=3 and cms[2][0]=="'"):
				cms[2]=hex(ord(cms[2][1:-1]))[2:]
			if(cms[0] in self.tb_commands):
				if(self.debug>1):
					print("compiling '{0}' as {1} (len should be 3)  ".format(line,cms))
				if(len(cms)<3):
					raise SemanticError("Command '{0}' needs 2 args, got {1} (line: {2})".format(cms[0],len(cms),cms))
				cm_block,arg1_block,arg2_block=self.compile_tb_command(cms)
				self.compiled[(self.startname,self.current_object,self.blockno)]=cm_block
				self.blockno+=1
				self.compiled[(self.startname,self.current_object,self.blockno)]=arg1_block
				self.blockno+=1
				self.compiled[(self.startname,self.current_object,self.blockno)]=arg1_block
				self.blockno+=1
				self.lineno+=1
				continue

	def compile_tb_command(self,arr):
		# this will allow the at&t ptr handling with ``mov (ptr) addr''
		if("pmov" in self.tb_commands):
			if(cms[0]=="mov" and cms[1][0]=="("):
				if(self.debug>0):
					print(" interpreting {0} as pmov".format(line))
				cms[0]="pmov"
				cms[1]=cms[1][1:cms[1].index(")")]
				if(DEBUG):
					print("  new line: {0}".format(" ".join(cms)))

		if("movp" in self.tb_commands):
			if(cms[0]=="mov" and cms[2][0]=="("):
				if(self.debug):
					print(" interpreting {0} as movp".format(line))
				cms[0]="movp"
				cms[2]=cms[2][1:cms[2].index(")")]
				if(self.debug):
					print("  new line: {0}".format(" ".join(cms)))
		# XXX ATTENTION!
		# we make no difference here between static symbolic names and non static symbolic names.
		# I do not know if this will work out later. :-(
		arg1=0
		arg2=0
		if(cms[0] in self.support_symbolic_names):
			try:
				arg1=int(cms[1])
			except ValueError:
				arg1=cms[1]
		else:
			try:
				arg1=int(cms[1])
			except ValueError:
				raise SemanticError("command {} needs integer argument; found: '{}'".format(cms[0],cms[1]))
			if(arg1>=



