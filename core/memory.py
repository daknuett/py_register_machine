"""
A python-only implementation of the PyRegisterMachine's
memory module.
Using numpy.array as a memory representation.
"""
from ctypes import *
import os,time,sys
import numpy as np

sfr_callbacks = {}


class HaltException(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)

class Register(object):
	def __init__(self,nmbr,*args):
		self.nmbr = nmbr
		self._repr = np.zeros(1, dtype = np.int64) 
	def read(self):
		return self._repr[0]
	def write(self,val):
		self._repr[0] = val
class StdRegister(Register):
	def __init__(self, nmbr, *args):
		Register.__init__(self, nmbr, *args)

class OutPutRegister(Register):
	def __init__(self, nmbr, stream_name, *args):
		Register.__init__(self,nmbr,*args)
		open_stream = None
		if((stream_name == "stdout") or (stream_name == "/dev/stdout")):
			open_stream = sys.stdout
		else:
			open_stream = open(stream_name, "w")
			
		self.stream = open_stream
	def read(self):
		return Register.read(self)
	def write(self, val):
		Register.write(self, val)
		ch = None
		try:
			ch = chr(val)
		except:
			ch = "?"
		self.stream.write(ch)
	
		
class SpecialFunctionRegister(Register):
	def __init__(self, nmbr, *args):
		Register.__init__(self, nmbr, *args)
	def write(self, val):
		if(val in sfr_callbacks):
			sfr_callbacks[val]()
		Register.write(self, val)

class IORegister(Register):
	def __init__(self, nmbr, callback_read, callback_write, *args):
		Register.__init__(self, nmbr, *args)
		def read_none():
			return self._repr[0]
		def write_none(val):
			return
		if(not hasattr(callback_read, "__call__")):
			self.callback_read = read_none
		else:
			self.callback_read = callback_read
		if(not hasattr(callback_write, "__call__")):
			self.callback_write = write_none
		else:
			self.callback_write = callback_write
	def write(self, val):
		self.callback_write(val)
		Register.write(self, val)
	def read(self):
		return self.callback_read()


register_types = {3: StdRegister, 2: OutPutRegister, 1: SpecialFunctionRegister, 4: IORegister}
		 
class Registers(object):
	@staticmethod
	def from_string(string):
		res = []
		num_regs = string[:string.index("/")]
		regs = string[string.index("/") + 1:]
		for reg_descr in regs.split(";"):
			if(reg_descr == ""):
				break
			number, _type, data = reg_descr.split(",")
			res.append(register_types[int(_type)](int(number), data, (None,None)))
		return res
				

class Ram(object):
	""""""
	@staticmethod
	def from_str(_str, callback_exit = None):
		size,registers = _str.split("|")
		register_count = int(registers[:registers.index("/")])
		return Ram(int(size), registers = registers,
				register_count = register_count,
				_callback_exit = callback_exit)

	def __init__(self,
			size,
			registers = "10/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;",
			register_count = 10,
			stacksize = 20, 
			_callback_exit = None):
		def callback_exit():
			print("exiting.")
			sys.exit(0)
			return 0

		if(_callback_exit == None):
			_callback_exit = callback_exit
		self.register_string = registers

		self.size = size
		if(registers != None):
			register_reprs = Registers.from_string(registers)
		else:
			register_reprs = []

		self.registers = register_reprs

		self._repr = np.zeros(self.size, dtype = np.int64)
		self.add_SFR_callback(0xff, _callback_exit)

		def hw_print_int():
			print(self.read(0))
		def ram_dump():
			self.dump()

		self.add_SFR_callback(0x04,hw_print_int)
		self.add_SFR_callback(0x05,ram_dump)
		# for halt without sys.exit:
		self.nexttime_halt = False
		def halt_cpu(*args):
			self.nexttime_halt = True
		# halt the cpu
		self.add_SFR_callback(0xfe,halt_cpu)

		# we need the number of registers
		self.reg_cnt = register_count
		# a stack for push
		self.stack=[ [] for i in range(self.reg_cnt)]
		# stack size and usage
		self.stacksize = stacksize
		self.stackusage = 0
	def __del__(self):
		del(self.registers)
		del(self._repr)

	def set_io_functions_at(self, _iter, io_functs):
		self.registers[_iter].callback_write, self.registers[_iter].callback_write = io_functs

	def read(self, _iter):
		if(_iter >= self.size):
			_iter = self.size - 1
		if(self.nexttime_halt):
			raise HaltException()
		if(_iter < self.reg_cnt):
			return self.registers[_iter].read()
		return self._repr[_iter]
	def write(self, _iter, value):
		if(_iter >= self.size):
			_iter = self.size - 1
		if(self.nexttime_halt):
			raise HaltException()
		if(_iter < self.reg_cnt):
			return self.registers[_iter].write(value)
		else:
			self._repr[_iter] = value

	def add_SFR_callback(self,operation_number,callback):
		sfr_callbacks[operation_number] = callback
	def __getitem__(self,_iter):
		return self.read(_iter)
	def __setitem__(self,_iter,ele):
		self.write(_iter,ele)
	def __str__(self):
		return "< {0} object >:\n{2} {1} {3}".format(Ram.__qualname__, self.dumps(), "{", "}")
	def dump(self,fname=None):
		if(fname==None):
			fname=str(time.time()).encode("ascii")
		with open(fname, "w") as f:
			f.write(self.dumps())
			f.close()
	def dumps(self):
		dumps=""
		for addr in range(self.size):
			dumps += "{}\t{}\n".format(format(addr,"x"), format(self.read(addr),"x"))
		return dumps
	def pushr(self,nmbr):
		if(self.nexttime_halt):
			raise HaltException()
		if(nmbr >= self.reg_cnt):
			return
		self.stack[nmbr].append(self.read(nmbr))
		# nasty: stack has to be fixed sized (see definition of DFA)
		# so this will overwrite the last element
		if(len(self.stack) > self.stacksize):
			self.stack = self.stack[:self.stacksize]
		self.stackusage = len(self.stack)
	def popr(self,nmbr):
		if(self.nexttime_halt):
			raise HaltException()
		if(nmbr >= self.reg_cnt):
			return
		try:
			self.write(nmbr,self.stack[nmbr].pop())
		except IndexError:
			self.write(nmbr,0)
	def definition_string(self):
		return "{}|{}".format(self.size, self.register_string)


class Flash(object):
	def __init__(self, size, std_savename = "flash.save", saved=False):
		self.std_savename = std_savename
		self.size = size
		if(saved == False):
			self._repr = np.zeros(self.size, dtype = np.int64)
		else:
			self._repr = Flash._from_file(std_savename)
	@staticmethod
	def _from_file(fname):
		res = []
		with open(fname, "r") as f:
			size = f.readline()
			for line in f.read().split("\n"):
				if(line == ""):
					break
				offset, word = line.split()
				res.append(int(word, 16))
			f.close()
		return np.array(res, dtype = np.int64)
	def __del__(self):
		del(self._repr)
	def read(self,_iter):
		if(_iter >= self.size):
			_iter = self.size - 1
		return self._repr[_iter]
	def write(self, _iter, value):
		if(_iter >= self.size):
			_iter = self.size - 1
		self._repr[_iter] = value
	def __dump__(self,fname):
		with open(fname, "w") as f:
			f.write(self.dumps())
			f.close()
	def dump(self,fname=None):
		if(fname==None):
			self.__dump__(self.std_savename)
		else:
			self.__dump__(fname.encode("ascii"))
	def dumps(self):
		s = str(self.size) + "\n"
		for offset, word in enumerate(self._repr):
			s += "{}\t{}\n".format(format(offset, "x"), format(word, "x"))
		return 	s
	def __str__(self):
		return "< {0} object >:\n{2} {1}{3}".format(Flash.__qualname__, self.dumps(), "{", "}")

if (__name__=="__main__"):
	r=Ram(100,registers="11/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;",register_count=11)

	r.read(10)
#r.write(10,10)
