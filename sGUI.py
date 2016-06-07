import sys

from core.memory import *
from core.processor import *
from extra.basic_graph import *
from tools.assembler import *

from tkinter import *
from tkinter.messagebox import *

class RegisterGui(Frame):
	def __init__(self,processor,master=None,*args):
		self.show_debug=True
		self.exec_start_point=processor.PC # for resetting the processor.
		Frame.__init__(self,master)
		self.l1=Label(self.master,text="Operations",font="bold")
		self.l2=Label(self.master,text="Assembly",font="bold")
		self.l3=Label(self.master,text="Ram",font="bold")
		self.l4=Label(self.master,text="Flash",font="bold")
		self.l1.grid(row=0,column=0,padx=0)
		self.l2.grid(row=0,column=1,padx=40)
		self.l3.grid(row=0,column=3,padx=40)
		self.l4.grid(row=0,column=5,padx=40)
		self.asm_text=Text(self.master  ,height=30,width=60)
		self.ram_text=Text(self.master  ,height=30,width=30)
		self.flash_text=Text(self.master,height=30,width=30)
		self.scroll_asm=Scrollbar(self.master  ,command=self.asm_text.yview)
		self.scroll_ram=Scrollbar(self.master  ,command=self.ram_text.yview)
		self.scroll_flash=Scrollbar(self.master,command=self.flash_text.yview)
		self.asm_text.grid(row=1,column=1)
		self.ram_text.grid(row=1,column=3)
		self.flash_text.grid(row=1,column=5)

		self.asm_text.configure(yscrollcommand=self.scroll_asm.set)
		self.ram_text.configure(yscrollcommand=self.scroll_ram.set) 
		self.flash_text.configure(yscrollcommand=self.scroll_flash.set)

		self.scroll_asm.grid(row=1,column=2)
		self.scroll_ram.grid(row=1,column=4)
		self.scroll_flash.grid(row=1,column=6)

		self.l5=Label(self.master,text="LCD")
		self.l5.grid(row=2,column=1,padx=10)
		self.processor=processor

		self.lcd_gui=BasicGraphics(processor.ram,10,11,root=self.master,using_in_gui=True)
		self.lcd=self.lcd_gui.canvas
		self.lcd.grid(row=3,column=1)

		self.step_button=Button(self.master,text="do step",command=self.do_step)
		self.step_button.grid(row=2,column=0)
		self.file_label=Label(self.master,text="Filename")
		self.file_name=Entry(self.master)
		self.file_save_button=Button(self.master,text="Save File", command=self.save_file)
		self.file_load_button=Button(self.master,text="Load File",command=self.load_file)
		self.assemble_help_label=Label(self.master,text="Save the file, assemble it and program the current flash")
		self.assemble_button=Button(self.master,text="Assemble File",command=self.assemble_file)
		self.file_label.grid(row=4,column=0)
		self.file_name.grid(row=5,column=0)
		self.file_save_button.grid(row=6,column=0)
		self.file_load_button.grid(row=7,column=0)
		self.assemble_help_label.grid(row=8,column=0)
		self.assemble_button.grid(row=9,column=0)
	def refresh_ram(self):
		self.ram_text.delete("1.0",END)
		self.ram_text.insert(INSERT,self.processor.ram.dumps())
	def refresh_flash(self):
		self.flash_text.delete("1.0",END)
		flash_text=self.processor.flash.dumps()
		self.flash_text.insert(INSERT,flash_text[flash_text.index("\n"):])
	def do_step(self):
		try:
			self.processor.__process__(self.processor.PC)
		except JMPException:
			pass
		except HaltException:
			showwarning("sGui","Execution reached halt point.")
			self.processor.PC=self.exec_start_point
			self.processor.ram.nexttime_halt=False
			self.lcd_gui.reset()
			return
		except BaseException as e:
			showwarning("sGui",str(e))
			return
		self.refresh_flash()
		self.refresh_ram()
	def save_file(self):
		name=self.file_name.get()
		if(name==""):
			showwarning("sGui","Need filename!")
		_file=open(name,"w")
		text=self.asm_text.get("1.0",END)
		_file.write(text)
		_file.close()
	def load_file(self):
		name=self.file_name.get()
		if(name==""):
			showwarning("sGui","Need filename!")
		text=""
		try:
			_file=open(name,"r")
			text=_file.read()
			_file.close()
		except:
			showwarning("sGui","File does not exits. loading empty string")
		self.asm_text.delete("1.0",END)
		self.asm_text.insert(INSERT,text)
	def assemble_file(self):
		name=self.file_name.get()
		self.save_file()
		p=Preprocessor(name)
		try:
			p.do_all()
		except BaseException as e:
			showwarning("sGui",str(e))
			return
		asm=Assembler(self.processor,name+".pr")
		try:
			total,used=asm.compile()
			if(used>total):
				raise BaseException("Error: program flash too small")
		except BaseException as e:
			showwarning("sGui",str(e))
			return
		if(self.show_debug):
			showwarning("sGui","assembling successfull\n{} of {} blocks used: {} %".format(used,total,(used/total)*100))
		os.system("rm -f "+name+"\.pr*")	



if __name__=="__main__":
	r=Ram(400,registers="12/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;11,4,n;",register_count=12)
	f=Flash(1000)
	p=Processor(r,f)
	r=RegisterGui(p,master=Tk(className="py register machine"))
	mainloop()
