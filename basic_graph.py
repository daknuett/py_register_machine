from memory import *

import tkinter as tk
from processor import *

import sys

class BasicGraphics(object):
	def __init__(self,memory,chr_reg_nmbr,cursor_reg_nmbr):
		self.memory=memory
		self.root=None
		self.canvas=None
		self.cursor=0
		self.max_per_line=40
		self.max_lines=15
		self.chr_reg_nmbr=chr_reg_nmbr
		self.cursor_reg_nmbr=cursor_reg_nmbr
		self.current_display=[" "*self.max_per_line for x in range(self.max_lines)]
		self.displayed_lines=[]
		self.align_l=10
		self.h_diff=15
		self.store_to_protect_against_garbage_collection=[]
		def start_x():
			self.root=tk.Tk()
			self.canvas=tk.Canvas(self.root,bg="black")
			self.canvas.pack()
			for line in self.current_display:
				self.displayed_lines.append(self.canvas.create_text(self.align_l,self.h_diff*(self.cursor //10 +1 ),text=line,fill="white",anchor="nw"))
			self.canvas.delete("all")
			self.canvas.update()

		def display_lines():
			self.canvas.delete("all")
			self.canvas.update()
			self.displayed_lines=[]
			lineno=1
			for line in self.current_display:
				self.displayed_lines.append(self.canvas.create_text(self.align_l,lineno*self.h_diff*(self.cursor //10 +1 ),text=line,fill="white",anchor="nw"))
				lineno+=1
			self.canvas.update()
		def set_cursor(reg,cursor):
			self.cursor=cursor
			return 0
		def putc(reg,char):
			pos=self.cursor
			h=pos//10
			w=pos%51
			ch=char
			self.current_display[h]=self.current_display[h][0:w]+chr(ch)+self.current_display[h][w+1:]
			display_lines()
			return 0
		def get_cursor(*args):
			return self.cursor
		def mainloop_exit(*args):
			tk.mainloop()
			sys.exit()
		start_x()
		c_putc=IO_FUNCT_WRITE(putc)
		c_do_null=IO_FUNCT_READ(do_null)
		self.store_to_protect_against_garbage_collection.append(c_putc)
		self.store_to_protect_against_garbage_collection.append(c_do_null)
		self.memory.set_x_data_at(self.chr_reg_nmbr,self.memory.memlib.newIOFuncts(c_putc,c_do_null))
		c_set_cursor=IO_FUNCT_WRITE(set_cursor)
		c_get_cursor=IO_FUNCT_READ(get_cursor)
		self.memory.set_x_data_at(self.cursor_reg_nmbr,self.memory.memlib.newIOFuncts(c_set_cursor,c_get_cursor))
		self.store_to_protect_against_garbage_collection.append(c_set_cursor)
		self.store_to_protect_against_garbage_collection.append(c_get_cursor)
		self.memory.add_SFR_callback(0x05,SFR_COMM(mainloop_exit))

def do_null(*args):
	return 0
if __name__=="__main__":
	r=Ram(100,registers="12/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;11,4,n;",register_count=12)
	b=BasicGraphics(r,10,11)
	f=Flash(200,saved=True,std_savename=b"basic_graphics.flash")
	p=Processor(r,f)
	p.process()
	while(1):
		break





