"""
Bindings to memory.c,
in addition to this some more object orientation.
"""
from ctypes import *
import os,time,sys
from .shared_lib import shared_lib

SFR_COMM=CFUNCTYPE(c_void_p)
IO_FUNCT_READ=CFUNCTYPE(c_int,c_void_p)
IO_FUNCT_WRITE=CFUNCTYPE(c_int,c_void_p,c_int)

# for testing
#

def io_funct_r(reg):
	print(reg,"read")
	return 2
def io_funct_w(reg,val):
	print(reg,val)
	return 0
io_read=IO_FUNCT_READ(io_funct_r)
io_write=IO_FUNCT_WRITE(io_funct_w)


class HaltException(BaseException):
	def __init__(self,*args):
		BaseException.__init__(self,*args)

class Register(object):
	def __init__(self,nmbr,memlib_file_name,*args):
		self.nmbr=nmbr
		self.memlib=cdll.LoadLibrary(memlib_file_name)
		self._repr=None
	def read(self):
		ret=self.memlib.Register_read(self._repr)
		ret=c_int(ret)
		return ret.value
	def write(self,val):
		self.memlib.Register_write(self._repr,c_int(val))
class StdRegister(Register):
	def __init__(self,nmbr,memlib_file_name=shared_lib,*args):
		Register.__init__(self,nmbr,memlib_file_name,*args)
		self._repr=self.memlib.newStdRegister(c_uint(nmbr))
class OutPutRegister(Register):
	def __init__(self,nmbr,memlib_file_name=shared_lib,fname="stdout",*args):
		Register.__init__(self,nmbr,memlib_file_name,*args)
		fout=None
		if(fname=="stdout"):
			libc=CDLL("libc.so.6")
			fout=c_voidp.in_dll(libc,"stdout")
		if(fout==None):raise BaseException("no valid output stream!")
		self._repr=self.memlib.newOutPutRegister(c_uint(nmbr),fout)
class SpecialFunctionRegister(Register):
	def __init__(self,nmbr,memlib_file_name=shared_lib,*args):
		Register.__init__(self,nmbr,memlib_file_name,*args)
		self._repr=self.memlib.newSpecialFunctionRegister(c_uint(nmbr))

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
			memlib_file_name = shared_lib,
			stacksize = 20, 
			_callback_exit = None):
		def callback_exit():
			print("exiting.")
			del(self)
			sys.exit(0)
			return c_int(0)

		if(_callback_exit == None):
			_callback_exit = callback_exit
		self.register_string = registers

		self.memlib = cdll.LoadLibrary(memlib_file_name)
		self.size = size
		if(registers != None):
			register_reprs = self.memlib.Registers_from_string(c_char_p(registers.encode("ascii")));
		else:
			register_reprs = 0
		self._repr = self.memlib.newRam(c_size_t(size),register_reprs,register_count)
		self.callback_functs = []
		self.IO_functs = []	# protection against the goddammed garbage collection
		self.add_SFR_callback(0xff, SFR_COMM(_callback_exit))
		def hw_print_int():
			print("DEBUG:: hw_print_int()")
			print(self.read(0))
		def ram_dump():
			self.dump()
		self.add_SFR_callback(0x04,SFR_COMM(hw_print_int))
		self.add_SFR_callback(0x05,SFR_COMM(ram_dump))
		# for halt without sys.exit:
		self.nexttime_halt=False
		def __halt_cpu(*args):
			self.nexttime_halt=True
		halt_cpu=SFR_COMM(__halt_cpu)
		# halt the cpu
		self.add_SFR_callback(0xfe,halt_cpu)

		# we need the number of registers
		self.reg_cnt = register_count
		# a stack for push
		self.stack=[ [] for i in range(self.reg_cnt)]
		# stack size and usage
		self.stacksize=stacksize
		self.stackusage=0
	def __del__(self):
		self.memlib.delRam(self._repr)

	def read(self,_iter):
		if(self.nexttime_halt):
			raise HaltException()
		return c_int(self.memlib.Ram_read(self._repr,c_size_t(_iter))).value
	def write(self,_iter,value):
		if(self.nexttime_halt):
			raise HaltException()
		self.memlib.Ram_write(self._repr,c_size_t(_iter),value)

	def add_SFR_callback(self,operation_number,callback):
		all_callbacks=c_voidp.in_dll(self.memlib,"sfr_comms")
		my_callback=self.memlib.newSFRCommand(c_uint(operation_number),callback)
		new_all_callbacks=self.memlib.new_SFRCommandHolder(my_callback,all_callbacks)
		self.memlib.set_sfr_comms(new_all_callbacks)
		self.callback_functs.append(callback)
	def __getitem__(self,_iter):
		return self.read(_iter)
	def __setitem__(self,_iter,ele):
		self.write(_iter,ele)
	def __str__(self):
		dumps=""
		fname=str(time.time()).encode("ascii")
		self.memlib.Ram_dump(self._repr,fname)
		f=open(fname,"r")
		dumps=f.read()
		f.close()
		os.unlink(fname)
		return "< {0} object >:\n{2} {1} {3}".format(Ram.__qualname__,dumps,"{","}")
	def dump(self,fname=None):
		if(fname==None):
			fname=str(time.time()).encode("ascii")
		else:
			fname=fname.encode("ascii")
		self.memlib.Ram_dump(self._repr,fname)
	def dumps(self):
		name=str(time.time())
		self.dump(name)
		s=open(name).read()
		os.unlink(name)
		return s
	def pushr(self,nmbr):
		if(self.nexttime_halt):
			raise HaltException()
		if(nmbr>=self.reg_cnt):
			return
		self.stack[nmbr].append(self.read(nmbr))
		# nasty: stack has to be fixed sized (see definition of DFA)
		# so this will overwrite the last element
		if(len(self.stack)>self.stacksize):
			self.stack=self.stack[:self.stacksize]
		self.stackusage=len(self.stack)
	def popr(self,nmbr):
		if(self.nexttime_halt):
			raise HaltException()
		if(nmbr>=self.reg_cnt):
			return
		try:
			self.write(nmbr,self.stack[nmbr].pop())
		except IndexError:
			self.write(nmbr,0)
	def set_x_data_at(self,at,x_data):
		self.IO_functs.append(x_data)
		self.memlib.Ram_set_x_data_at(self._repr,c_uint(at),x_data)
	def definition_string(self):
		return "{}|{}".format(self.size, self.register_string)


class Flash(object):
	def __init__(self,size,memlib_file_name=shared_lib,std_savename=b"flash.save",saved=False):
		self.memlib=cdll.LoadLibrary(memlib_file_name)
		self.std_savename=std_savename
		self.size=size
		if(saved==False):
			self._repr=self.memlib.newFlash(c_size_t(size))
		else:
			self._repr=self.memlib.Flash_from_file(c_char_p(std_savename))
	def __del__(self):
		self.memlib.delFlash(self._repr)
	def read(self,_iter):
		return self.memlib.Flash_read(self._repr,c_size_t(_iter))
	def write(self,_iter,value):
		self.memlib.Flash_write(self._repr,c_size_t(_iter),c_int(value))
	def __dump__(self,fname):
		self.memlib.Flash_dump(self._repr,c_char_p(fname))
	def dump(self,fname=None):
		if(fname==None):
			self.__dump__(self.std_savename)
		else:
			self.__dump__(fname.encode("ascii"))
	def dumps(self):
		name=str(time.time())
		self.dump(name)
		s=open(name).read()
		os.unlink(name)
		return 	s
	def __str__(self):
		fname=str(time.time()).encode("ascii")
		self.__dump__(fname)
		f=open(fname,"r")
		dumps=f.read()
		f.close()
		os.unlink(fname)
		return "< {0} object >:\n{2} {1}{3}".format(Flash.__qualname__,dumps,"{","}")

if (__name__=="__main__"):
	r=Ram(100,registers="11/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;",register_count=11)

	r.set_x_data_at(10,r.memlib.newIOFuncts(io_write,io_read))
	r.read(10)
#r.write(10,10)
