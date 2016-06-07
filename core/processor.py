"""
execute commands to modify the data
"""
from .memory import *
import sys
from .processor_functions import *
import socket

DEFAULT_RAM_S = 160
DEFAULT_FLASH_S = 360
DEBUG = 0


"""
About Interrupts
################
Any Interrupt is an asynchronous coroutine in another thread or another process.

If the Interrupt is driven by a thread, it is an internal interrupt and will be called
using the ``processor.Processor.interrupt'' method.
This method will contact the main thread via socket and the main thread will handle the
interrupt

If the Interrupt is driven by another process (maybe on a remote host) it is an external
interrupt. This process will have to contact the main thread via socket and transmit the
interrupt name. TODO: implement external interrupts.

Implementation in the Processor
###############################
The Processor stores all interrupts by name and address in the program memory.
If an interrupt is caused, the Processor object will stop the normal execution
and go to the address of the interrupt. There has to be either a call of an interrupt handle
or a ``ret'':

    @interrupt foo
    icall foo_handle

or
    @interrupt bar
    ret

The interrupt addresses start at the end of flash - 1 and grow to the beginning of the flash.
For every interrupt 4 words are reserved:

    3df    11     | second registered interrupt: ret
    3e0    0    
    3e1    0
    3e2    0
    3e3    1f     | first registered interrupt: icall
    3e4    192    | address of interrupt handle
    3e5    11     | ret
    3e6    0      | 4th interrupt word
    3e7    0      | pad word and last memory address



About Internal Interrupts
#########################
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


class SIGSEGV(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)
class JMPException(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)


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
	@staticmethod
	def from_str(_str):
		# doing this using a csv interpreter would be
		# just an overkill.
		members = _str.split("|")
		ram_str = "|".join(members[:2])
		fl_size = int(members[2])
		tb_commands = eval(members[3])
		db_commands = eval(members[4])
		sg_commands = eval(members[5])
		commands = eval(members[6])
		return Processor(ram = Ram.from_str(ram_str), 
				flash = Flash(fl_size),
				tb_commands = tb_commands,
				db_commands = db_commands,
				sg_commands = sg_commands,
				commands = commands)
	def __init__(self, ram = None,
			flash = None,
			tb_commands = None,
			db_commands = None,
			sg_commands = None,
			interrupt_desciptors = [],
			commands = ALL_FUNCTIONS,
			interrupt_disable_functions = [], # to disable Timers on exit
			*args):

		self.commands = []
		self.interrupt_disable_functions = interrupt_disable_functions

		for name,function in commands:
			self.register_function(name,function)


		# proper cleanup...
		def callback_exit():
			print("exit.")
			del(self.ram)
			del(self.flash)
			for function in self.interrupt_disable_functions:
				function()
			sys.exit(0)
			return c_int(0)
		self.callback_exit = callback_exit


		if(ram == None):
			self.ram = Ram(DEFAULT_RAM_S, _callback_exit = self.callback_exit)
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
				0x21:"pjgt",0x22:"pjge",
				0x1f:"xor"}
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

		self.PC = self.ram.size  # used to move over the memory, starting at first flash block
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
	def register_function(self, name, funct):
		if(DEBUG):
			print("DEBUG:: registering {} ::= {}".format(name, funct.__qualname__))
		self.commands.append((name, funct.__qualname__))
		setattr(self, name, funct)

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
		def refactored_names(list_with_commands):
			_str = "["
			for command in list_with_commands:
				_str += "('{}',{}),".format(command[0], command[1])
			_str = _str[:-1]
			_str += "]"
			return _str
		return "{0}| {1}| {2}| {3}| {4}| {5}".format(self.ram.definition_string(),
				self.flash.size,
				self.tb_commands,
				self.db_commands,
				self.sg_commands,
				refactored_names(self.commands))
	def __dump__(self,fname):
		f=open(fname,"w")
		f.write(self.__dumps__()+"\n")
		f.close()
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
		if(DEBUG > 6):
			print("DEBUG::[static][jmp]({})".format(self.PC))
		self.traceback.append((oldloc,self.PC))
		raise JMPException(str(oldloc))


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
			if(com in self.sg_commands):
				print("--word[{}]: {} (= <{}>)".format(ptr,_ptr_loc.read(ptr),self.sg_commands[com]))
			elif(com in self.db_commands):
				print("--word[{}]: {} (= <{}>) <{}>".format(ptr,
							_ptr_loc.read(ptr),
							self.db_commands[com],
							_ptr_loc.read(ptr + 1)))
			elif(com in self.tb_commands):
				print("--word[{}]: {} (= <{}>) <{}> <{}>".format(ptr,
							_ptr_loc.read(ptr),
							self.tb_commands[com],
							_ptr_loc.read(ptr+1),
							_ptr_loc.read(ptr+2)))
		self.abs_comms += 1
		if(com in self.sg_commands):
			self.stddef[self.sg_commands[com]](self)
			self.PC+=1
			return 1
		if(com in self.db_commands):
			self.stddef[self.db_commands[com]](self, _ptr_loc.read(ptr + 1))
			self.PC+=2
			self.loads += 1
			return 2
		if(com in self.tb_commands):
			self.stddef[self.tb_commands[com]](self, _ptr_loc.read(ptr + 1),_ptr_loc.read(ptr + 2))
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
