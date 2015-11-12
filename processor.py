"""
execute commands to modify the data
"""
from memory import *

DEFAULT_RAM_S=160
DEFAULT_FLASH_S=360
DEBUG=False

class SIGSEGV(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)
class JMPException(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)

def Processor_from_str(_str):
	# doing this using a csv interpreter would be
	# just an overkill.
	members=_str.split(";")
	rm_size=int(members[0])
	fl_size=int(members[1])
	tb_commands=eval(members[2])
	db_commands=eval(members[3])
	sg_commands=eval(members[4])
	return Processor(ram=Ram(rm_size), flash=Flash(fl_size),tb_commands=tb_commands,db_commands=db_commands,sg_commands=sg_commands)



class Processor(object):
	from_str=Processor_from_str
	def __init__(self,ram=None,flash=None,tb_commands=None,db_commands=None,sg_commands=None,*args):
		if(ram==None):
			self.ram=Ram(DEFAULT_RAM_S)
		else:
			self.ram=ram
		if(flash==None):
			self.flash=Flash(DEFAULT_FLASH_S)
		else:
			self.flash=flash
		if(tb_commands==None):
			self.tb_commands={0x1:"mov",0x2:"add",0x3:"sub",0x4:"mul",0x5:"ldi",0xa:"jgt",0xb:"subi",0xc:"addi",0xd:"jle",0xe:"jeq",0xf:"jne",0x10:"jlt",0x13:"jge",0x14:"mod",0x15:"modi",0x16:"div",0x19:"pmov",0x1a:"movp"}
		else:
			self.tb_commands=tb_commands
		if(db_commands==None):
			self.db_commands={0x6:"inc",0x7:"dec",0x8:"neg",0x12:"call",0x17:"pop",0x18:"push"}
		else:
			self.db_commands=db_commands
		if(sg_commands==None):
			self.sg_commands={0x9:"nop",0x11:"ret"}
		else:
			self.sg_commands=sg_commands
		self.PC=0 # used to move over the memory
		self.total_pc=0 # complete number of memory movements
		self.loc=self.ram.size # the current ptr for __process__ placed at the beginning of the flash.
		self.stddef={"mov":self.mov,"add":self.add,"sub":self.sub,"mul":self.mul,"div":self.div,"ldi":self.ldi,"addi":self.addi,"subi":self.subi,"or":self._or,"xor":self.xor,"and":self._and,"ori":self.ori,"xori":self.xori,"andi":self.andi,"neg":self.neg,"inc":self.inc,"dec":self.dec,"jmp":self.jmp,"pjmp":self.pjmp,"jne":self.jne,"pjne":self.pjne,"jeq":self.jeq,"pjeq":self.pjeq,"jle":self.jle,"pjle":self.pjle,"jlt":self.jlt,"pjlt":self.pjlt,"jgt":self.jgt,"pjgt":self.pjgt,"jge":self.jge,"pjge":self.pjge,"nop":self.nop,"call":self.call,"ret":self.ret,"mod":self.mod,"modi":self.modi,"pop":self.pop,"push":self.push,"pmov":self.pmov,"movp":self.movp}
		self.stack=[]
	def __dumps__(self):
		return "{0}; {1}; {2}; {3}; {4};".format(self.ram.size,self.flash.size,self.tb_commands,self.db_commands,self.sg_commands)
	def __dump__(self,fname):
		f=open(fname,"w")
		f.write(self.__dumps__()+"\n")
		f.close()
	def mov(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in))
	def movp(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_out=_to.read(_out)
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size

		_to.write(_out,_from.read(_in))
	def pmov(self,_in,_out): # mov from the ptr in _in to _out
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_in=_from.read(_in)

		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size

		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in))

	def add(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)+_to.read(_out))
	def mod(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)%_to.read(_out))
	def modi(self,_in,_out):	
		_from=self.ram
		if(_out>=self.ram.size):
			_from=self.flash
			_out-=self.ram.size
		_from.write(_out,_in%_from.read(_out))

	def sub(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)-_to.read(_out))
	def addi(self,_in,_out):
		_from=self.ram
		if(_out>=self.ram.size):
			_from=self.flash
			_out-=self.ram.size
		_from.write(_out,_in+_from.read(_out))

	def subi(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_in-_to.read(_out))
	def mul(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)*_to.read(_out))
	def div(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)//_to.read(_out))
	def ldi(self,_in,_out):
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_in)
	def inc(self,_inout):
		_to=self.ram
		if(_inout>=self.ram.size):
			_to=self.flash
			_inout-=self.ram.size
		_to.write(_inout,_to.read(_inout)+1)
	def dec(self,_inout):
		_to=self.ram
		if(_inout>=self.ram.size):
			_to=self.flash
			_inout-=self.ram.size
		_to.write(_inout,_to.read(_inout)-1)
	def neg(self,_inout):
		_to=self.ram
		if(_inout>=self.ram.size):
			_to=self.flash
			_inout-=self.ram.size
		_to.write(_inout,_to.read(_inout)*-1)
	def __jmp__(self,ptr):
		""" move the ptr to a new place """
		oldloc=(self.loc,self.PC)
		self.loc=ptr
		self.total_pc+=self.PC
		self.PC=0
		raise JMPException(str(oldloc))
	def jmp(self,loc):
		self.__jmp__(loc)
	def pjmp(self,_in):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		self.__jmp__(_from.read(_in))
	def pjne(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		if(_from.read(_in)!=0):
			self.__jmp__(_to.read(_out))
	def jne(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		if(_from.read(_in)!=0):
			self.__jmp__(_to)
	def pjeq(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		if(_from.read(_in)==0):
			self.__jmp__(_to.read(_out))
	def jeq(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		if(_from.read(_in)==0):
			self.__jmp__(_to)
	def pjge(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		if(_from.read(_in)>=0):
			self.__jmp__(_to.read(_out))
	def jge(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		if(_from.read(_in)>=0):
			self.__jmp__(_to)
	def pjle(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		if(_from.read(_in)<=0):
			self.__jmp__(_to.read(_out))
	def jle(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		if(_from.read(_in)<=0):
			self.__jmp__(_to)
	def pjgt(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		if(_from.read(_in)>0):
			self.__jmp__(_to.read(_out))
	def jgt(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		if(_from.read(_in)>0):
			self.__jmp__(_to)
	def pjlt(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		if(_from.read(_in)<0):
			self.__jmp__(_to.read(_out))
	def jlt(self,_in,_to):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		if(_from.read(_in)<0):
			self.__jmp__(_to)
	def xor(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)^_to.read(_out))
	def _or(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)|_to.read(_out))
	
	def _and(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_from.read(_in)&_to.read(_out))

	def xori(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to.write(_out,_in^_to.read(_out))
	def ori(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_in|_to.read(_out))
	
	def andi(self,_in,_out):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		_to=self.ram
		if(_out>=self.ram.size):
			_to=self.flash
			_out-=self.ram.size
		_to.write(_out,_in&_to.read(_out))
	def nop(self):
		pass

	def call(self,ptr):
		self.stack.append((self.loc,self.PC))
		self.__jmp__(ptr)
	def ret(self):
		old_loc,old_pc=self.stack.pop()
		old_real_head=old_loc+old_pc
		self.__jmp__(old_real_head+2)

	def pop(self,reg):
		self.ram.popr(reg)
	def push(self,reg):
		self.ram.pushr(reg)

	def process(self):
		""" start above HIGH_RAMEND to execute. 
			This is flash[0]."""
		while(1):
			try:
				self.__process__(self.loc)
			except SIGSEGV as e: # something  bad happened
				self.ram.dump()
				raise e
			except JMPException:
				continue




	def __process__(self,ptr):
		ptr+=self.PC
		_ptr_loc=self.ram
		real_addr=ptr
		if(ptr>=self.ram.size):
			_ptr_loc=self.flash
			ptr-=self.ram.size
		com=_ptr_loc.read(ptr)
		if(DEBUG):
			try:
				print(_ptr_loc.read(ptr),self.sg_commands[com])
			except:
				try:
					print(_ptr_loc.read(ptr),self.db_commands[com],_ptr_loc.read(ptr+1))
				except:
					try:
						print(_ptr_loc.read(ptr),self.tb_commands[com],_ptr_loc.read(ptr+1),_ptr_loc.read(ptr+2))
					except:
						pass
		if(com in self.sg_commands):
			self.stddef[self.sg_commands[com]]()
			self.PC+=1
			return 1
		if(com in self.db_commands):
			self.stddef[self.db_commands[com]](_ptr_loc.read(ptr+1))
			self.PC+=2
			return 2
		if(com in self.tb_commands):
			self.stddef[self.tb_commands[com]](_ptr_loc.read(ptr+1),_ptr_loc.read(ptr+2))
			self.PC+=3
			return 3
		raise SIGSEGV("invalid command ({0}) (memory: {1} (= {2} ) real addr: {3} (= {4} ))  (correct compiler?)".format(com,hex(ptr),ptr,hex(real_addr),real_addr))

	

if(__name__=="__main__"):
	f=Flash(360,saved=True)
	p=Processor(flash=f)
	try:
		p.process()
	except BaseException as e:
		print(e)
