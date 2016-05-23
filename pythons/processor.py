"""
execute commands to modify the data
"""
from memory import *

DEFAULT_RAM_S = 160
DEFAULT_FLASH_S = 360
DEBUG = 5


"""
To provide stable interrupts a socketpair is used.
``socket.socketpair()'' provides such a pair of connected sockets.
There is one socket for the main thread/process, which is stored in
the processor.Processor object, the other socket can be used by other
threads to start any kind of interrupt.

The Interrupt will be transmitted in the following format:
	interrupt :=	address';';
	address :=	x{x};
	x := 	'0'|'1'|...|'f';

"""

import socket

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

class Interrupt(object):
	def __init__(self, address, name, processor_callback = None):
		self.address = address
		self.name = name
		self.processor_callback = processor_callback
	def __call__(self):
		try:
			self.processor_callback(self.address)
		except JMPException:
			pass
	@staticmethod
	def from_descriptor_and_processor(descriptor,processor):
		return Interrupt(processor.get_interrupt_address(),
				descriptor.name,
				processor.interrupt)

class InterruptDescriptor(object):
	def __init__(self, name, runnable_at_init = None):
		self.name = name
		self.runnable_at_init = runnable_at_init
	



class Processor(object):
	from_str=Processor_from_str
	def __init__(self, ram = None,
			flash = None,
			tb_commands = None,
			db_commands = None,
			sg_commands = None,
			interrupt_desciptors = [],
			*args):
		if(ram == None):
			self.ram = Ram(DEFAULT_RAM_S)
		else:
			self.ram = ram
		if(flash == None):
			self.flash = Flash(DEFAULT_FLASH_S)
		else:
			self.flash = flash
		if(tb_commands == None):
			self.tb_commands = {0x1:"mov",0x2:"add",
				0x3:"sub",0x4:"mul",
				0x5:"ldi",0xa:"jgt",
				0xb:"subi",0xc:"addi",
				0xd:"jle",0xe:"jeq",
				0xf:"jne",0x10:"jlt",
				0x13:"jge",0x14:"mod",
				0x15:"modi",0x16:"div",
				0x19:"pmov",0x1a:"movp",
				0x1d:"pjeq",0x1e:"pjne",
				0x1f:"pjlt",0x20:"pjle",
				0x21:"pjgt",0x22:"pjge"}
		else:
			self.tb_commands = tb_commands
		if(db_commands == None):
			self.db_commands = {0x6:"inc",0x7:"dec",
				0x8:"neg",0x12:"call",
				0x17:"pop",0x18:"push",
				0x1b:"jmp",0x1c:"pjmp",
				0x1d:"icall"}
		else:
			self.db_commands = db_commands
		if(sg_commands == None):
			self.sg_commands = {0x9:"nop",0x11:"ret",0x24:"fdump"}
		else:
			self.sg_commands = sg_commands
		self.PC = self.ram.size # used to move over the memory, starting at first flash block
		self.stddef = {"mov":self.mov,"add":self.add,
			"sub":self.sub,"mul":self.mul,
			"div":self.div,"ldi":self.ldi,
			"addi":self.addi,"subi":self.subi,
			"or":self._or,"xor":self.xor,
			"and":self._and,"ori":self.ori,
			"xori":self.xori,"andi":self.andi,
			"neg":self.neg,"inc":self.inc,
			"dec":self.dec,"jmp":self.jmp,
			"pjmp":self.pjmp,"jne":self.jne,
			"pjne":self.pjne,"jeq":self.jeq,
			"pjeq":self.pjeq,"jle":self.jle,
			"pjle":self.pjle,"jlt":self.jlt,
			"pjlt":self.pjlt,"jgt":self.jgt,
			"pjgt":self.pjgt,"jge":self.jge,
			"pjge":self.pjge,"nop":self.nop,
			"call":self.call,"ret":self.ret,
			"mod":self.mod,"modi":self.modi,
			"pop":self.pop,"push":self.push,
			"pmov":self.pmov,"movp":self.movp,
			"fdump":self.fdump, "icall":self.icall}
		self.abs_comms = 0
		self.loads = 0
		self.stack = []
		self.traceback = []
		# the interrupt addresses are the very last addresses
		# pay attention: they might be overwritten by too big programs
		# FIXME: adapt the assembler to this feature
		self.current_interrupt_pointer =  self.ram.size + self.flash.size - 1
		self.interrupts = []
		for inter in interrupt_desciptors:
			self.register_interrupt(inter)
		self.main_socket, self.subthread_socket = socket.socketpair()
		# this is now the F_CPU by the way....
		self.main_socket.settimeout(0.1)

	def get_interrupt_address(self):
		# leave 4 words for any call
		self.current_interrupt_pointer -= 4
		return self.current_interrupt_pointer 

	def _interrupt(self, address):
		if(DEBUG > 2):
			print("DEBUG:: _interrupt({})".format(address))
		self.stack.append(self.PC)
		self.__jmp__(address, static = True, addrspace_inflash = False)
	def interrupt(self, address):
		if(DEBUG > 2):
			print("DEBUG:: interrupt({})".format(address))
		hex_address = hex(address)[2:]
		total_transmission = hex_address + ';'
		_bytes = total_transmission.encode("utf-8")
		transmitted = self.subthread_socket.send(_bytes)
		if(transmitted != len(_bytes)):
			raise Exception("Failed to send interrupt signal")
	def register_interrupt(self, interrupt_descriptor):
		new_interrupt = Interrupt.from_descriptor_and_processor(interrupt_descriptor,self)
		if(interrupt_descriptor.runnable_at_init != None):
			interrupt_descriptor.runnable_at_init(new_interrupt)
		self.interrupts.append(new_interrupt)
	def interrupt_address_from_name(self, name, flash_address = False):
		for interrupt in self.interrupts:
			if(interrupt.name == name):
				if(DEBUG):
					print("DEBUG:: flash.size = ",self.flash.size)
					print("DEBUG:: interrupt address flash: {} real: {}".format(interrupt.address - self.ram.size, interrupt.address))
				if(flash_address):
					return interrupt.address - self.ram.size
				return interrupt.address


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
		try:
			_to.write(_out,_from.read(_in)//_to.read(_out))
		except ZeroDivisionError:
			_to.write(_out,0)
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
	def __jmp__(self, ptr, static = False, addrspace_inflash = False ):
		""" move the ptr to a new place """
		oldloc = self.PC
		if(addrspace_inflash):
			ptr += self.ram.size
			if(DEBUG):
				print("adding {} to __jmp__ ptr".format(self.ram.size))
		if(static):
			if(DEBUG):
				print("__jmp__ to ",ptr)
			self.PC = ptr
		else:
			self.PC+=ptr # relative!!
		if(DEBUG > 3):
			print("DEBUG::[static][jmp]({})".format(self.PC))
		self.traceback.append((oldloc,self.PC))
		raise JMPException(str(oldloc))
	def jmp(self,loc):
		self.__jmp__(loc)
	def pjmp(self,_in):
		_from=self.ram
		if(_in>=self.ram.size):
			_from=self.flash
			_in-=self.ram.size
		self.__jmp__(_from.read(_in))
	def pjne(self,_in,_out):
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
	def pjeq(self,_in,_out):
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
	def pjge(self,_in,_out):
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
	def pjle(self,_in,_out):
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
	def pjgt(self,_in,_out):
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
	def pjlt(self,_in,_out):
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
		if(DEBUG > 3):
			print("DEBUG::call({})".format(ptr)) 
		self.stack.append(self.PC)
		self.__jmp__(ptr)
	def ret(self):
		old_pc=self.stack.pop()
		# here we need static jumping! 
		self.__jmp__(old_pc+2,static=True) # +2 args of call

	def pop(self,reg):
		try:
			self.ram.popr(reg)
		except IndexError:
			raise SIGSEGV("Pop from empty stack! memory: {0} ( = {1} ) real: {2} ( = {3} ) traceback: {4}".format(hex(self.PC-self.ram.size),self.PC-self.ram.size,hex(self.PC),self.PC,self.traceback))
	# for savings
	#
	def fdump(self):
		self.flash.dump()
	def push(self,reg):
		self.ram.pushr(reg)

	# call at the interrupt handle:
	# usage:
	#     @interrupt foo
	#     icall foo_interrupt_handle
	#     ret
	def icall(self, address):
		self.stack.append(self.PC)
		self.__jmp__(address, static = True, addrspace_inflash = False)


	def process(self):
		""" start above HIGH_RAMEND to execute. 
			This is flash[0]."""
		while(1):
			try:
				self.__process__(self.PC)
			except SIGSEGV as e: # something  bad happened
				self.ram.dump()
				raise e
			except JMPException:
				continue
			except HaltException: # to hat the processor without sys.exit
				break




	def __process__(self,ptr):
		# check for incoming interrupt request
		request = self.incoming_interrupt_request()
		if(request):
			self._interrupt(int(request,16))

		_ptr_loc = self.ram
		real_addr = ptr
		if(ptr >= self.ram.size):
			_ptr_loc = self.flash
			ptr -= self.ram.size
		com=_ptr_loc.read(ptr)
		if(DEBUG > 3):
			try:
				print(ptr,_ptr_loc.read(ptr),self.sg_commands[com])
			except:
				try:
					print(ptr,_ptr_loc.read(ptr),self.db_commands[com],_ptr_loc.read(ptr+1))
				except:
					try:
						print(ptr,_ptr_loc.read(ptr),self.tb_commands[com],_ptr_loc.read(ptr+1),_ptr_loc.read(ptr+2))
					except:
						pass
		self.abs_comms += 1
		if(com in self.sg_commands):
			self.stddef[self.sg_commands[com]]()
			self.PC+=1
			return 1
		if(com in self.db_commands):
			self.stddef[self.db_commands[com]](_ptr_loc.read(ptr+1))
			self.PC+=2
			self.loads += 1
			return 2
		if(com in self.tb_commands):
			self.stddef[self.tb_commands[com]](_ptr_loc.read(ptr+1),_ptr_loc.read(ptr+2))
			self.PC+=3
			self.loads += 2
			return 3
		raise SIGSEGV("invalid command ({0}) (memory: {1} (= {2} ) real addr: {3} (= {4} ))  (correct compiler?)\ntraceback: {5}".format(com,hex(ptr),ptr,hex(real_addr),real_addr,self.traceback))
	def incoming_interrupt_request(self):
		chunks = b''
		value = ""
		try:
			chunks = self.main_socket.recv(1)
		except:
			return None
		while(chunks != b';'):
			value += chunks.decode("utf-8")
			chunks = self.main_socket.recv(1)
		return value

	

if(__name__=="__main__"):
	f=Flash(360,saved=True)
	p=Processor(flash=f)
	try:
		p.process()
	except BaseException as e:
		print(e)
