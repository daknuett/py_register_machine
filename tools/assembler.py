from ..core.memory import *
from ..core.processor import *
import string


STD_INC_PATH = "./py_register_machine/assemblys/"
DEBUG = True

""" use an assembly file to programm the flash. """


class Preprocessor(object):
	def __init__(self,fname):
		self.in_file=open(fname,"r")
		self.out_file=open(fname+".pr","w")
		self.symbols={}
		self.unprocessed=self.in_file.read()
		self.lines=self.unprocessed.split("\n")
	def strip_comments(self):
		new_lines=[]
		for line in self.lines:
			if(line.startswith(";")):
				continue
			if(line.isspace()):
				continue
			new_lines.append(line)
		self.lines=new_lines
	def include_files(self):
		includes=[]
		imports=[]
		for line in self.lines:
			if(line.startswith("#include")):
				includes.append(line)
			if(line.startswith("#import")):
				imports.append(line)
		for inc in includes:
			fname=""
			inc=inc[8:]
			if(inc[0]=='"'):
				fname=inc[1:-1]
			elif(inc[0]=="<"):
				fname=STD_INC_PATH+inc[1:-1]
			else:
				raise InvalidSyntaxError(inc)
			f=open(fname)
			new_lines=f.read().split("\n")
			self.lines=new_lines+self.lines
		for imp in imports:
			fname=""
			imp=imp[7:]
			if(imp[0]=='"'):
				fname=imp[1:-1]
			elif(imp[0]=="<"):
				fname=STD_INC_PATH+imp[1:-1]
			else:
				raise InvalidSyntaxError(imp)
			f=open(fname)
			new_lines=f.read().split("\n")
			self.lines=self.lines+new_lines
	def process_definitions(self):
		new_lines=[]
		for line in self.lines:
			new_line=[]
			for word in line.split():
				if(word in self.symbols):
					new_line.append(self.symbols[word])
					if(DEBUG):
						print("DEBUG:: preprocessor: substituting <{0}> with <{1}>".format(word,self.symbols[word]))
				else:
					new_line.append(word)
			line=" ".join(new_line)
			if(line.startswith("#define")):
				args=line.split()
				self.symbols[args[1]]=" ".join(args[2:])
				continue
			if(line.startswith("#include")):
				continue
			if(line.startswith("#import")):
				continue
			new_lines.append(line)
		self.lines=new_lines
	def write(self):
		self.out_file.write("\n".join(self.lines))
	def do_all(self):
		self.include_files()
		self.process_definitions()
		self.strip_comments()
		self.write()
		self.in_file.close()
		self.out_file.close()
			
				


class InvalidSyntaxError(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)
class SemanticError(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)


class Assembler(object):
	def __init__(self,processor,fname):
		self.processor=processor
		prepr=Preprocessor(fname)
		prepr.do_all()
		self.f=open(fname+".pr","r")
		self.lines=self.f.read().split("\n")
		self.symbols={} # the addresses
		self.symbol_refs={} # for relative addresses we need the current address
		self.word_count=0
		# symbolic names are dereferenced by the assembler
		self.support_symbolic_names=["jmp","call","jne","jeq","jle","jge","jlt","jgt"]
		self.support_static_symbolic_names=["mov","ldi","icall"]
		self.static_symbols={}
		self.i_commands=["ldi","addi","subi","xori","ori","andi","modi"]
		self.commands={v:k for k,v in self.processor.tb_commands.items()}
		self.commands.update({v:k for k,v in self.processor.db_commands.items()})
		self.commands.update({v:k for k,v in self.processor.sg_commands.items()})
		self.tb_commands={v:k for k,v in self.processor.tb_commands.items()}
		self.db_commands={v:k for k,v in self.processor.db_commands.items()}
		self.sg_commands={v:k for k,v in self.processor.sg_commands.items()}

		self.flag_skipline = False
		self.interrupts = {}
	def compile(self):
		if(DEBUG):
			print("DEBUG::flash.size = ",self.processor.flash.size) 
		compiled=[]
		for lineno,line in enumerate(self.lines):
			compiled.extend(self.compileline(lineno,line,self.lines))
		# DONE with syntax and mnemonic parsing
		# NOW: generating the references
		#
		#
		#
		for k,v in self.symbols.items():
			if(v=="?"):
				raise UnboundReferenceError("{0} not referenced!(references: {1})".format(k,self.symbols))
		new_compiled = []
		if(DEBUG):
			print("DEBUG:: symbol references:",self.symbol_refs)
			print("DEBUG:: symbols:",self.symbols)
			print("DEBUG:: static symbols:",self.static_symbols)
		for address, word in enumerate(compiled):
			if(word in self.symbols):
				orig = word # saving the  word for further operations
				if(DEBUG):
					print("||word[{0}] adding reference ({3}) (abs: {1} || rel: {2})".format(address,
								self.symbols[word],
								self.symbols[word] - ( (address) + self.processor.ram.size),
								word))
				word = self.symbols[word] - ( (address) + self.processor.ram.size)
				 # took me about 3 h reading disassembly, to find this bug.
				 # we have to skip the arguments +_+ 
				calls = self.symbol_refs[orig]
				for call in calls:
					if(DEBUG):
						print("DEBUG:: call:",call)
					if( call[0] + 1 == address or call[0] + 2 == address):
						if(DEBUG):
							print("DEBUG:: (word {2})adding offset of {0}: {1}".format(call[1], call[2], call[0]))
						word += call[2]
			if(word in self.static_symbols):
				if(self.static_symbols[word]=="?"):
					raise UnboundReferenceError("{0} not referenced!(static references: {1})".format(word,self.static_symbols))
				word=self.static_symbols[word]
			new_compiled.append(word)
		for address, word in enumerate(new_compiled):
			if(isinstance(word,int)):
				self.processor.flash.write(address, word)
			else:
				self.processor.flash.write(address, int(word, 16))
		# write the interrupt handlers
		if(DEBUG):
			print("DEBUG::interrupts: ",self.interrupts)
		for address, handle in self.interrupts.items():
			# append a ret
			handle.append(0x11)
			if(DEBUG):
				print("DEBUG::interrupts:: ({}|{})".format(address, handle))
			for _iter,content in enumerate(handle):
				if(isinstance(content, int)):
					if(DEBUG):
						print("DEBUG::writing to address {} : {}".format(address + _iter, content))
					self.processor.flash.write(address + _iter, content)
				else:

					if(content in self.symbols):
						self.processor.flash.write(address + _iter,self.symbols[content])
					else:
						raise UnboundReferenceError("{0} not referenced!(references: {1})".format(content,self.symbols))
		return (self.processor.flash.size,self.word_count)



	def compileline(self,lineno,line,lines):
		compiled = []
		if(self.flag_skipline):
			self.flag_skipline = False
			return []
		else:
			if(DEBUG):
				print('||word[{1},...]: compiling line "{0}"'.format(line,self.word_count))
			cms=line.split()
			if(len(cms)==0):
				return []
			# support characters (eg for prints)
			if(len(cms)>=2 and cms[1][0]=="'"):
				cms[1]=hex(ord(cms[1][1:-1]))[2:] # as we are using still strings ;-)
			if(len(cms)>=3 and cms[2][0]=="'"):
				cms[2]=hex(ord(cms[2][1:-1]))[2:]
			# support preassembled arithmetics
			if(len(cms)>=2 and cms[1][0]=="["):
				if(DEBUG):
					print("DEBUG::",cms)
					print("DEBUG::",line)
				cms[0]=cms[0]
				cms[1]=line[line.index("["):line.index("]")+1]
				cms[2]=line[line.index("]")+1:]
				cms=cms[:3]
				line=line[line.index("]")+1:]
				if(DEBUG):
					print("DEBUG::",cms)
				cms[1]=hex(eval(cms[1][1:-1]))[2:]
			if(len(cms)>=3 and cms[2][0]=="["):
				cms[2]=line[line.index("["):line.index("]")+1]
				cms[2]=hex(eval(cms[2][1:-1]))[2:]
				cms=cms[:3]

			if(cms[0] in self.tb_commands):
				if(DEBUG):
					print("C|word[{0}, {1}, {2}] compiling as command(len=3)".format(self.word_count,
								self.word_count + 1,
								self.word_count + 2))
				if(len(cms)!=3):
					raise SemanticError("command {0} wants 2 args, but got {1}: {2}".format(cms[0],len(cms),line))
				# this will allow the at&t ptr handling with ``mov (ptr) addr''
				if("pmov" in self.tb_commands):
					if(cms[0]=="mov" and cms[1][0]=="("):
						if(DEBUG):
							print("|- interpreting <{0}> as pmov".format(line))
						cms[0]="pmov"
						cms[1]=cms[1][1:cms[1].index(")")]
						if(DEBUG):
							print("|-- new line: <{0}>".format(" ".join(cms)))

				if("movp" in self.tb_commands):
					if(cms[0]=="mov" and cms[2][0]=="("):
						if(DEBUG):
							print("|- interpreting <{0}> as movp".format(line))
						cms[0]="movp"
						cms[2]=cms[2][1:cms[2].index(")")]
						if(DEBUG):
							print("|-- new line: <{0}>".format(" ".join(cms)))

				compiled.extend(self.compile_tb_command(cms))
				self.word_count+=3
			elif(cms[0] in self.db_commands):
				if(DEBUG):
					print("C|word[{0}, {1}] compiling as command(len=2)".format(self.word_count,
								self.word_count + 1))
				compiled.extend(self.compile_db_command(cms))
				self.word_count+=2
			elif(cms[0] in self.sg_commands):
				if(DEBUG):
					print("C|word[{0}] compiling as command(len=1)".format(self.word_count))
				if(len(cms)!=1):
					raise SemanticError("command {0} wants 0 args, but got {1}: {2}".format(cms[1],len(cms),line))
				try:
					compiled.append(self.commands[cms[0]])
				except KeyError:
					raise SyntaxError("{0}: command not found!".format(cms[0]))
				self.word_count+=1
			# addressing of jump marks
			#
			#
			elif(cms[0][-1]==":"):
				if(DEBUG):
					print("S|word[{1}] compiling as symbol :: SYM<{0}>".format(cms[0][:-1], self.word_count))
				if(cms[0][:-1] in self.symbols):
					if(self.symbols[cms[0][:-1]] != "?"):
						raise SemanticError("{0}: multiple definitions of symbol!".format(cms[0]))
					else:
						self.symbols[cms[0][:-1]] = self.processor.ram.size + self.word_count
				else:
					self.symbols[cms[0][:-1]] = self.processor.ram.size + self.word_count
					self.symbol_refs[cms[0][:-1]] = []
			# new: datasetting
			#
			elif(cms[0]==".set"):
				if(self.word_count==0):
					raise SemanticError("(memory {0}): [{1}]: program has to start with program, not with data!".format(self.word_count,line))
				if(DEBUG):
					print("D|word[{1}] setting data (name: {0}) : {2}".format(cms[1],self.word_count,cms[2]))
				# for characters
				if(cms[2][0]=="'"):
					cms[2]=ord(cms[2][1:2])
				compiled.append(cms[2])
				self.static_symbols[cms[1]]=self.word_count+self.processor.ram.size
				self.word_count+=1
			# new: strings
			# usage: .string <name> "string"
			# will add a null terminated in the flash and add a reference to the first char
			# use it like a c string with pointer arithmethic.
			elif(cms[0]==".string"):
				if(self.word_count==0):
					raise SemanticError("(memory {0}): [{1}]: program has to start with program, not with data!".format(self.word_count,line))
				_str=" ".join(cms[2:])[1:-1] # strip ""
				strlen=len(_str)+1 # null
				self.static_symbols[cms[1]]=self.word_count+self.processor.ram.size
				if(DEBUG):
					print("D|word[{1},...] setting string (name: {0}) : {2}".format(cms[1],self.word_count,_str))
				i=0
				while( i < len(_str)):
					compiled.append(ord(_str[i]))
					if(DEBUG):
						print("adding string literal ",compiled[-1])
					i+=1
				compiled.append(0)
				self.word_count += strlen
			# new: interrupts
			# TODO: update wiki
			elif(cms[0] == "@interrupt"):
				interrupt_name = cms[1]
				interrupt_call = self.compileline(lineno + 1,lines[lineno + 1],lines)
				self.flag_skipline = True
				address = self.processor.interrupt_address_from_name(interrupt_name, flash_address = True)
				self.interrupts[address] = interrupt_call
			else:
				raise SyntaxError("{0}: not an expression!\n avaiable commands: {1}".format(line,self.commands))
			return compiled


	def compile_tb_command(self,cms):
		compiled = []
		first_arg_is_number = False
		second_arg_is_number = False

		try:
			int(cms[1], 16)
			first_arg_is_number = True
		except:
			pass
		try:
			int(cms[2], 16)
			second_arg_is_number = True
		except:
			pass

		# command does not support any symbols:
		if( (not cms[0] in self.support_static_symbolic_names) and
			(not cms[0] in self.support_symbolic_names) and
			(False in (second_arg_is_number, first_arg_is_number))):
				raise SemanticError("{0} or {1} not a valid address or number".format(cms[1],cms[2]))

		# check for valid addresses
		if( (not cms[0] in self.i_commands) and first_arg_is_number):
			addr = int(cms[1], 16)
			if( (addr > self.processor.ram.size + self.processor.flash.size) or
					(addr < 0)):
				raise SemanticError("{0}: not a valid address!".format(cms[1]))
		# the second argument is __always__ an address!
		if(second_arg_is_number):
			addr = int(cms[2], 16)
			if( (addr > self.processor.ram.size + self.processor.flash.size) or
					(addr < 0)):
				raise SemanticError("{0}: not a valid address!".format(cms[2]))
		

		# Now everything should be valid:
		# Actually compile the command and the args.
		# If an arg is not a number check for symbols.
		compiled_command = None
		try:
			compiled_command = self.tb_commands[cms[0]]
		except:
			raise SyntaxError("{0}: command not found!".format(cms[0]))
		compiled.append(compiled_command)

		# compile first arg
		if(first_arg_is_number):
			compiled.append(int(cms[1], 16))
		else:
			if(cms[0] in self.support_static_symbolic_names):
				if( cms[1] not in  self.static_symbols):
					self.static_symbols[cms[1]] = "?"
			elif(cms[0] in self.support_symbolic_names):
				# check for symbols
				if(cms[1] in self.symbols):
					# storing the reference like this:
					# (lineno, caller, offset)
					# The offset is needed because every argunemt has its own word.
					self.symbol_refs[cms[1]].append((self.word_count, cms[0], 1 ))
				else:
					self.symbols[cms[1]]="?"
					self.symbol_refs[cms[1]]=[(self.word_count, cms[0], 1)]

			else:
			 	raise SemanticError("{0} does not support symbolic names!".format(cms[0]))
			compiled.append(cms[1])



		if(second_arg_is_number):
			compiled.append(int(cms[2], 16))
		else:
			if(cms[0] in self.support_static_symbolic_names):
				# dereferencing symbols is done later
				if( cms[2] not in  self.static_symbols):
					self.static_symbols[cms[2]] = "?"
			elif(cms[0] in self.support_symbolic_names):
				if(cms[2] in self.symbols):
					self.symbol_refs[cms[2]].append((self.word_count, cms[0], 2 ))
				else:
					self.symbols[cms[2]]="?"
					self.symbol_refs[cms[2]]=[(self.word_count, cms[0], 2)]
			else:
			 	raise SemanticError("{0} does not support symbolic names!".format(cms[0]))
			compiled.append(cms[2])
		return compiled




	def compile_db_command(self, cms):
		compiled = []
		arg_is_number = False
		try:
			int(cms[1], 16)
			arg_is_number = True
		except:
			pass

		if( not arg_is_number and 
			(not cms[0] in self.support_symbolic_names) and
			(not cms[0] in self.support_static_symbolic_names)):
			raise SemanticError("{0} does not support symbolic names!".format(cms[0]))
		if(arg_is_number and 
			(not cms[0] in self.i_commands) and
			(not int(cms[1], 16) in range(0, self.processor.ram.size + self.processor.flash.size))):
			raise SemanticError("{0}: not a valid address!".format(cms[1]))

		compiled_command = None
		try:
			compiled_command = self.db_commands[cms[0]]
		except:
			raise SyntaxError("{0}: command not found!".format(cms[0]))
		compiled.append(compiled_command)

		if(arg_is_number):
			compiled.append(int(cms[1], 16))
		else:
			if(cms[0] in self.support_static_symbolic_names):
				if( cms[1] not in  self.static_symbols):
					self.static_symbols[cms[1]] = "?"
			elif(cms[0] in self.support_symbolic_names):
				if(cms[1] in self.symbols):
					self.symbol_refs[cms[1]].append((self.word_count, cms[0], 1 ))
				else:
					self.symbols[cms[1]]="?"
					self.symbol_refs[cms[1]]=[(self.word_count, cms[0], 1)]

			else:
			 	raise SemanticError("{0} does not support symbolic names!".format(cms[0]))
			compiled.append(cms[1])
		return compiled

class UnboundReferenceError(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)
	


if(__name__=="__main__"):
	pr=Preprocessor("test.asm")
	pr.do_all()
	p=Processor()
	a=Assembler(p,"test.asm.pr")
	total,used=a.compile()
	print("{} of {} blocks used: {} %".format(used,total,(used/total)*100))
	p.flash.dump("flash_fib.save")
	p.process()
	p.ram.__dump__("ram.dump")
