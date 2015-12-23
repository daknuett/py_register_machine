from memory import *
from processor import *
from assembler import *


class LinkableAssembler(object):
	def __init__(self,processor,fname,startname,debug=0,data_sec_name="_data",*args):
		self.processor = processor
		prepr = Preprocessor(fname)
		prepr.do_all()
		# use the preprocessed file.
		self.f = open(fname+".pr","r")
		self.lines = self.f.read().split("\n")
		self.f.close()
		os.system("rm -f "+fname+"\.pr*")
		self.compiled = {}
		self.debug = debug
		self.lineno = 0
		self.blockno = 0
		self.data_sec_name=data_sec_name

		# from assembler.Assembler
		# symbolic names are dereferenced by the assembler
		self.support_symbolic_names = ["jmp","call","jne","jeq","jle","jge","jlt","jgt"]
		self.support_static_symbolic_names = ["mov","ldi"]
		self.i_commands = ["ldi","addi","subi","xori","ori","andi","modi"]
		# XXX NEW: some mnemonics support only register indices !
		self.register_only = ["add","sub","mul","div","mod","and","or","xor","neg","inc","dec"]

		# now the address space:
		# highest register index
		self.register_hi = self.processor.ram.reg_cnt
		# complete address space:
		self.addr_space = self.processor.ram.size + self.processor.flash.size

		self.commands = {v:k for k,v in self.processor.tb_commands.items()}
		self.commands.update({v:k for k,v in self.processor.db_commands.items()})
		self.commands.update({v:k for k,v in self.processor.sg_commands.items()})

		self.tb_commands = {v:k for k,v in self.processor.tb_commands.items()}
		self.db_commands = {v:k for k,v in self.processor.db_commands.items()}
		self.sg_commands = {v:k for k,v in self.processor.sg_commands.items()}

		self.current_object = startname
		self.startname=startname

		self.prev=startname

		self.static_symbols={}

	def compile(self):
		""" compiling relocatable is a bit more difficult.
			We need to save a lot more data to do this.
			So the layout is as following:
			{(startname,objectname,blockno):block}
			this allows rearranging of blocks by a linker. """
		for line in self.lines:
			# check for too big programs: 
			if(self.blockno >= self.processor.flash.size):
				raise SemanticError("too big program: flashsize: {} ".format(self.processor.flash.size))


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
			if(len(cms) >= 2 and cms[1][0] == "'"):
				cms[1] = hex(ord(cms[1][1:-1]))[2:] # as we are using still strings ;-)
			if(len(cms) >= 3 and cms[2][0] == "'"):
				cms[2] = hex(ord(cms[2][1:-1]))[2:]
			if(cms[0] in self.tb_commands):
				if(self.debug>1):
					print("compiling '{0}' as {1} (len should be 3)  ".format(line,cms))
				if(len(cms)<3):
					raise SemanticError("Command '{0}' needs 2 args, got: {1} \nline: '{2}'".format(cms[0],len(cms)," ".join(cms)))
				cm_block,arg1_block,arg2_block = self.compile_tb_command(cms)
				self.compiled[(self.startname,self.current_object,self.blockno,self.prev)]=cm_block
				self.blockno += 1
				self.compiled[(self.startname,self.current_object,self.blockno,self.prev)]=arg1_block
				self.blockno += 1
				self.compiled[(self.startname,self.current_object,self.blockno,self.prev)]=arg2_block
				self.blockno += 1
				self.lineno += 1
				continue
			if(cms[0] in self.db_commands):
				if(self.debug>1):
					print("compiling '{0}' as {1} (len should be 2)  ".format(line,cms))
				if(len(cms)<2):
					raise SemanticError("Command '{0}' needs 1 arg, got: {1} \nline: '{2}'".format(cms[0],len(cms)," ".join(cms)))
				cm_block,arg1_block=self.compile_db_command(cms)
				self.compiled[(self.startname,self.current_object,self.blockno,self.prev)]=cm_block
				self.blockno += 1
				self.compiled[(self.startname,self.current_object,self.blockno,self.prev)]=arg1_block
				self.blockno += 1
				self.lineno += 1
				continue
			if(cms[0] in self.sg_commands):
				if(self.debug>1):
					print("compiling '{0}' as {1} (len should be 1)  ".format(line,cms))
				if(len(cms)<1):
					raise SemanticError("Command '{0}' needs 0 args, got: {1} \nline: '{2}'".format(cms[0],len(cms)," ".join(cms)))
				cm_block=self.compile_sg_command(cms)
				self.compiled[(self.startname,self.current_object,self.blockno,self.prev)]=cm_block
				self.blockno += 1
				self.lineno += 1
				continue
			if(cms[0][-1] == ":"):
				self.prev=self.current_object
				self.current_object = cms[0][:-1]
				self.lineno += 1
				continue
			if(cms[0] == ".set"):
				self.static_symbols[cms[1]] = self.blockno
				self.compiled[(self.startname,self.data_sec_name,self.blockno,self.prev)] = int(cms[2],16)
				self.blockno += 1
			if(cms[0] == ".string"):
				self.static_symbols[cms[1]] = self.blockno
				string=" ".join(cms[2:])[1:-1]  # join blanks and strip " 
				for char in string:
					self.compiled[(self.startname,self.data_sec_name,self.blockno,self.prev)] = ord(char)
					self.blockno+=1
			raise SemanticError("ERROR: command not found: {}; lineno: {} \nline: '{}'".format(cms[0],self.lineno," ".join(cms)))
		return (self.compiled,self.static_symbols,self.blockno)

				


	def compile_tb_command(self,cms):
		# this will allow the at&t ptr handling with ``mov (ptr) addr''
		if("pmov" in self.tb_commands):
			if(cms[0] == "mov" and cms[1][0] == "("):
				if(self.debug>0):
					print(" interpreting {0} as pmov".format(line))
				cms[0] = "pmov"
				cms[1] = cms[1][1:cms[1].index(")")]
				if(DEBUG):
					print("  new line: {0}".format(" ".join(cms)))

		if("movp" in self.tb_commands):
			if(cms[0] == "mov" and cms[2][0] == "("):
				if(self.debug):
					print(" interpreting {0} as movp".format(line))
				cms[0] = "movp"
				cms[2] = cms[2][1:cms[2].index(")")]
				if(self.debug):
					print("  new line: {0}".format(" ".join(cms)))
		# XXX ATTENTION!
		# we make no difference here between static symbolic names and non static symbolic names.
		# I do not know if this will work out later. :-(
		arg1 = 0
		arg2 = 0

		# parse arg1
		if(cms[0] in self.support_symbolic_names or cms[0] in self.support_static_symbolic_names):
			try:
				arg1 = int(cms[1],16)
			except ValueError:
				arg1 = cms[1]
		else:
			try:
				arg1 = int(cms[1],16)
			except ValueError:
				raise SemanticError("command {} needs integer argument; found: '{}'; lineno: {}\nline: '{}'".format(
						cms[0],cms[1],self.lineno," ".join(cms)))
			if((arg1 < 0 or  arg1 >= self.addr_space ) and not cms[0] in self.i_commands ):
				raise SemanticError("argument has to be in address space ({}) ; invalid: '{}' lineno: {}\nline: '{}'".format(
						self.addr_space,arg1,self.lineno," ".join(cms)))
			if(arg1 >= self.register_hi and cms[0] in register_only):
				raise SemanticError("command {} has to be used with registers. highest register index: {} got: {} lineno:{}\nline: '{}'".format(
						cms[0],self.register_hi,arg1,self.lineno," ".join(cms)))


		# parse arg2
		if(cms[0] in self.support_symbolic_names or cms[0] in self.support_static_symbolic_names):
			try:
				arg2 = int(cms[2],16)
			except ValueError:
				arg2 = cms[2]
		else:
			try:
				arg2 = int(cms[2],16)
			except ValueError:
				raise SemanticError("command {} needs integer argument; found: '{}'; lineno: {}\nline: '{}'".format(
						cms[0],cms[2],self.lineno," ".join(cms)))
			if((arg2 < 0 or  arg2 >= self.addr_space ) and not cms[0] in self.i_commands ):
				raise SemanticError("argument has to be in address space ({}) ; invalid: '{}' lineno: {}\nline: '{}'".format(
						self.addr_space,arg2,self.lineno," ".join(cms)))
			if(arg2 >= self.register_hi and cms[0] in register_only):
				raise SemanticError("command {} has to be used with registers. highest register index: {} got: {} lineno:{}\nline: '{}'".format(
						cms[0],self.register_hi,arg2,self.lineno," ".join(cms)))

		command=self.commands[cms[0]]

		if(self.debug > 4):
			print(" {} => {} {} {}".format(" ".join(cms),command,arg1,arg2))
		return (command,arg1,arg2)

	def compile_db_command(self,cms):
		arg1 = 0
		# parse arg1
		if(cms[0] in self.support_symbolic_names or cms[0] in self.support_static_symbolic_names):
			try:
				arg1 = int(cms[1],16)
			except ValueError:
				arg1 = cms[1]
		else:
			try:
				arg1 = int(cms[1],16)
			except ValueError:
				raise SemanticError("command {} needs integer argument; found: '{}'; lineno: {}\nline: '{}'".format(
						cms[0],cms[1],self.lineno," ".join(cms)))
			if((arg1 < 0 or  arg1 >= self.addr_space ) and not cms[0] in self.i_commands ):
				raise SemanticError("argument has to be in address space ({}) ; invalid: '{}' lineno: {}\nline: '{}'".format(
						self.addr_space,arg1,self.lineno," ".join(cms)))
			if(arg1 >= self.register_hi and cms[0] in register_only):
				raise SemanticError("command {} has to be used with registers. highest register index: {} got: {} lineno:{}\nline: '{}'".format(
						cms[0],self.register_hi,arg1,self.lineno," ".join(cms)))


		command=self.commands[cms[0]]
		if(self.debug > 4):
			print(" {} => {} {}".format(" ".join(cms),command,arg1))			
		return (command,arg1)

	def compile_sg_command(self,cms):
		return self.commands[cms[0]]



if (__name__=="__main__"):
	r=Ram(400,registers="12/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;11,4,n;",register_count=12)
	f=Flash(1000)
	p=Processor(ram=r,flash=f)
		
	l=LinkableAssembler(p,"assemblys/prim.asm","start",debug=6)
	i,symbs,le=l.compile()
	print(le)
	for k,v in i.items():
		print(k,"\t\t",v)
