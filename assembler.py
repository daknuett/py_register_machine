from memory import *
from processor import *
import string

STD_INC_PATH="./"
DEBUG=False

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
		self.symbols={}
		self.line_count=0
		self.support_symbolic_names=["jmp","call","jne","jeq","jle","jge","jlt","jgt"]
		self.i_commands=["ldi","addi","subi","xori","ori","andi","modi"]
		self.commands={v:k for k,v in self.processor.tb_commands.items()}
		self.commands.update({v:k for k,v in self.processor.db_commands.items()})
		self.commands.update({v:k for k,v in self.processor.sg_commands.items()})
		self.tb_commands={v:k for k,v in self.processor.tb_commands.items()}
		self.db_commands={v:k for k,v in self.processor.db_commands.items()}
		self.sg_commands={v:k for k,v in self.processor.sg_commands.items()}
	def compile(self):
		compiled=[]
		for line in self.lines:
			if(DEBUG):
				print('{1} compiling line "{0}"'.format(line,self.line_count))
			cms=line.split()
			if(len(cms)==0):
				continue
			# support characters (eg for prints)
			if(len(cms)>=2 and cms[1][0]=="'"):
				cms[1]=hex(ord(cms[1][1:-1]))[2:] # as we are using still strings ;)
			if(len(cms)>=3 and cms[2][0]=="'"):
				cms[2]=hex(ord(cms[2][1:-1]))[2:]

			if(cms[0] in self.tb_commands):
				if(DEBUG):
					print("{0} compiling as command(len=3)".format(self.line_count))
				if(len(cms)!=3):
					raise SemanticError("command {0} wants 2 args, but got {1}: {2}".format(cms[0],len(cms),line))
				# this will allow the at&t ptr handling with ``mov (ptr) addr''
				if("pmov" in self.tb_commands):
					if(cms[0]=="mov" and cms[1][0]=="("):
						if(DEBUG):
							print(" interpreting {0} as pmov".format(line))
						cms[0]="pmov"
						cms[1]=cms[1][1:cms[1].index(")")]
						if(DEBUG):
							print("  new line: {0}".format(" ".join(cms)))

				if("movp" in self.tb_commands):
					if(cms[0]=="mov" and cms[2][0]=="("):
						if(DEBUG):
							print(" interpreting {0} as movp".format(line))
						cms[0]="movp"
						cms[2]=cms[2][1:cms[2].index(")")]
						if(DEBUG):
							print("  new line: {0}".format(" ".join(cms)))
				try:
					i=int(cms[1],16)
				except :
					raise SemanticError("{0}: not a valid address or number!".format(cms[1]))
				i=int(cms[1],16)
				if(i>self.processor.ram.size+self.processor.flash.size or i<0):
					if(cms[0] not in self.i_commands):
						raise SemanticError("{0}: not a valid address!".format(cms[1]))
				if((not cms[0] in self.support_symbolic_names)):
					try:
						i=int(cms[2],16)
						if(i<0 or i>self.processor.ram.size+self.processor.flash.size):
							raise ValueError()
					except:
						raise SemanticError("{0}: not a valid address!".format(cms[2]))
				else:
					_pass=False
					try:
						i=int(cms[2],16)
					except:
						if(cms[2] in self.symbols):
							if(self.symbols[cms[2]]!="?"):
								cms[2]=self.symbols[cms[2]]
						else:
							self.symbols[cms[2]]="?"
						_pass=True
					if(not _pass):
						i=int(cms[2])
					if(i<0 or i>self.processor.ram.size+self.processor.flash.size):
						raise SemanticError("{0}: not a valid address!".format(cms[2]))
				try:
					compiled.append(self.commands[cms[0]])
				except KeyError:
					raise SyntaxError("{0}: command not found!".format(cms[0]))
				compiled.append(cms[1])
				compiled.append(cms[2])
				self.line_count+=3
			elif(cms[0] in self.db_commands):
				if(DEBUG):
					print("{0} compiling as command(len=2)".format(self.line_count))
				if(len(cms)!=2):
					raise SemanticError("command {0} wants 1 arg, but got {1}: {2}".format(cms[1],len(cms),line))
				if(cms[0] in self.support_symbolic_names):
					if(cms[1] in self.symbols):
						
						if(self.symbols[cms[1]]!="?"):
							cms[1]=self.symbols[cms[1]]
					else:
						try:
							i=int(cms[1],16)
						except:
							self.symbols[cms[1]]="?"
						try:
							i=int(cms[1])
							if(i<0 or i>self.processor.ram.size+self.processor.flash.size):
								raise SemanticError("{0}: not a valid address!".format(cms[1]))
						except ValueError:
							pass
				else:
					try:
						i=int(cms[1],16)
						if(i<0 or i>self.processor.ram.size+self.processor.flash.size):
							raise ValueError
					except:
						raise SemanticError("{0}: not a valid address!".format(cms[1]))
				try:
					compiled.append(self.commands[cms[0]])
				except KeyError:
					raise SyntaxError("{0}: command not found!".format(cms[0]))
				compiled.append(cms[1])
				self.line_count+=2
			elif(cms[0] in self.sg_commands):
				if(DEBUG):
					print("{0} compiling as command(len=1)".format(self.line_count))
				if(len(cms)!=1):
					raise SemanticError("command {0} wants 0 args, but got {1}: {2}".format(cms[1],len(cms),line))
				try:
					compiled.append(self.commands[cms[0]])
				except KeyError:
					raise SyntaxError("{0}: command not found!".format(cms[0]))
				self.line_count+=1
			elif(cms[0][-1]==":"):
				if(DEBUG):
					print("{1} compiling as symbol {0}".format(cms[0][:-1],self.line_count))
				if(cms[0][:-1] in self.symbols):
					if(self.symbols[cms[0][:-1]] !="?"):
						raise SemanticError("{0}: multiple definitions of symbol!".format(cms[0]))
					else:
						self.symbols[cms[0][:-1]]=self.processor.ram.size+self.line_count
				else:
					self.symbols[cms[0][:-1]]=self.processor.ram.size+self.line_count
			else:
				raise SyntaxError("{0}: not an expression!\n avaiable commands: {1}".format(line,self.commands))

		for k,v in self.symbols.items():
			if(v=="?"):
				raise UnboundReferenceError("{0} not referenced!(references: {1})".format(k,self.symbols))
		new_compiled=[]
		for line in compiled:
			if(line in self.symbols):
				line=self.symbols[line]
			new_compiled.append(line)
		for i in range(len(new_compiled)):
			if(isinstance(new_compiled[i],int)):
				self.processor.flash.write(i,new_compiled[i])
			else:
				self.processor.flash.write(i,int(new_compiled[i],16))
		return (self.processor.flash.size,self.line_count)
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
