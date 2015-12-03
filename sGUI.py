from memory import *
from processor import *
from basic_graph import *

from tkinter import *

class RegisterGui(Frame):
	def __init__(self,processor,master=None,*args):
		Frame.__init__(self,master)
		self.l1=Label(self.master,text="Operations")
		self.l2=Label(self.master,text="Assembly")
		self.l3=Label(self.master,text="Ram")
		self.l4=Label(self.master,text="Flash")
		self.l1.grid(row=0,column=0,padx=40)
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
		self.refresh_flash()
		self.refresh_ram()

if __name__=="__main__":
	r=Ram(400,registers="12/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;11,4,n;",register_count=12)
	f=Flash(1000,saved=True,std_savename=b"basic_graphics.flash")
	p=Processor(r,f)
	r=RegisterGui(p,master=Tk(className="py register machine"))
	mainloop()
