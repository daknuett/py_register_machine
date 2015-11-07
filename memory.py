"""
Bindings to memory.c,
in addition to this some more object orientation.
"""
from ctypes import *
import os,time,sys

SFR_COMM=CFUNCTYPE(c_voidp)

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
	def __init__(self,nmbr,memlib_file_name="./libmemory.so",*args):
		Register.__init__(self,nmbr,memlib_file_name,*args)
		self._repr=self.memlib.newStdRegister(c_uint(nmbr))
class OutPutRegister(Register):
	def __init__(self,nmbr,memlib_file_name="./libmemory.so",fname="stdout",*args):
		Register.__init__(self,nmbr,memlib_file_name,*args)
		fout=None
		if(fname=="stdout"):
			libc=CDLL("libc.so.6")
			fout=c_voidp.in_dll(libc,"stdout")
		if(fout==None):raise BaseException("no valid output stream!")
		self._repr=self.memlib.newOutPutRegister(c_uint(nmbr),fout)
class SpecialFunctionRegister(Register):
	def __init__(self,nmbr,memlib_file_name="./libmemory.so",*args):
		Register.__init__(self,nmbr,memlib_file_name,*args)
		self._repr=self.memlib.newSpecialFunctionRegister(c_uint(nmbr))

class Ram(object):
	""""""
	def __init__(self,size,registers=b"4/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n",register_count=4,memlib_file_name="./libmemory.so"):
		self.memlib=cdll.LoadLibrary(memlib_file_name)
		self.size=size
		register_reprs=self.memlib.Registers_from_string(c_char_p(registers));
		self._repr=self.memlib.newRam(c_size_t(size),register_reprs,register_count)
		self.callback_functs=[]
		self.add_SFR_callback(0xff,SFR_COMM(callback_exit))
		def hw_print_int():
			print(self.read(0))
		self.add_SFR_callback(0x04,SFR_COMM(hw_print_int))
	def read(self,_iter):
		return c_int(self.memlib.Ram_read(self._repr,c_size_t(_iter))).value
	def write(self,_iter,value):
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

def callback_exit():
	print("exiting.")
	sys.exit(0)
	return c_int(0)

class Flash(object):
	def __init__(self,size,memlib_file_name="./libmemory.so",std_savename=b"flash.save",saved=False):
		self.memlib=cdll.LoadLibrary(memlib_file_name)
		self.std_savename=std_savename
		self.size=size
		if(saved==False):
			self._repr=self.memlib.newFlash(c_size_t(size))
		else:
			self._repr=self.memlib.Flash_from_file(c_char_p(std_savename))
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
	def __str__(self):
		fname=str(time.time()).encode("ascii")
		self.__dump__(fname)
		f=open(fname,"r")
		dumps=f.read()
		f.close()
		os.unlink(fname)
		return "< {0} object >:\n{2} {1}{3}".format(Flash.__qualname__,dumps,"{","}")

if (__name__=="__main__"):
	r=Ram(40,registers=b"4/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n",register_count=4)
#	r.add_SFR_callback(0xff,SFR_COMM(callback_exit))
	r.write(0x12,13)
	r.write(2,3+48)
	r.write(2,12)
	r.write(0x3,0xff)

