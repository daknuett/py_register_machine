"""
To avoid a mess in `processor.Processor` I have moved the functions to
this module.

The functions will have to be registered in the Processor.
"""

DEBUG = 0




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
def OR(self,_in,_out):
	_from=self.ram
	if(_in>=self.ram.size):
		_from=self.flash
		_in-=self.ram.size
	_to=self.ram
	if(_out>=self.ram.size):
		_to=self.flash
		_out-=self.ram.size
	_to.write(_out,_from.read(_in)|_to.read(_out))

def AND(self,_in,_out):
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




ALL_FUNCTIONS = [ ("mov", mov),
		("movp", movp),
		("pmov", pmov),
		("icall", icall),
		("push", push),
		("fdump", fdump),
		("pop", pop),
		("ret", ret),
		("call", call),
		("nop", nop),
		("andi", andi),
		("ori", ori),
		("xori", xori),
		("_and", AND),
		("_or", OR),
		("xor", xor),
		("jlt", jlt),
		("pjlt", pjlt),
		("jgt", jgt),
		("pjgt", pjgt),
		("jle", jle),
		("pjle", pjle),
		("jge", jge),
		("jeq", jeq),
		("pjeq", pjeq),
		("jne", jne),
		("pjne", pjne),
		("pjge", pjge),
		("pjmp", pjmp),
		("jmp", jmp),
		("neg", neg),
		("dec", dec),
		("inc", inc),
		("ldi", ldi),
		("div", div),
		("mul", mul),
		("subi", subi),
		("sub", sub),
		("addi", addi),
		("modi", modi),
		("mod", mod),
		("add", add)]
