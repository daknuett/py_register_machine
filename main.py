#!/usr/bin/python3

import sys


from .core.memory import *
from .core.processor import *
from .core.interrupts import *

use_gui = False
test_timer_en = False
if( use_gui):
	try:
		from extra.basic_graph import *
	except:
		print("warning: lcd alike graphics disabled (no python3-tk found)")
		print("install python3-tk or set ``main.use_gui = False'' to disable this warning")
		use_gui = False

# a complete ready to use register machine
# 

if __name__=="__main__":


	if(len(sys.argv)<=2):
		print("usage: {} <filename> <processor definition>".format(sys.argv[0]))
		sys.exit(-1)
	else:
		fname = sys.argv[1]
		fil = open(fname,"r")
		flash_size = int(fil.readline())
		fil.close()
		f = Flash(flash_size, std_savename = fname.encode(), saved = True)
		definition_file = open(sys.argv[2], "r")
		p = Processor.from_str(definition_file.read())
		definition_file.close()

		ram_definition = p.ram.definition_string()

		del(p.ram)
		# resetup the ram with a proper exit fucntion
		p.ram = Ram.from_str(ram_definition, callback_exit = p.callback_exit)
		p.flash = f

		if(use_gui):
			g = BasicGraphics(r,10,11)
		p.register_interrupt(timer0_interrupt_descriptor)
		p.register_interrupt(watchdog_interrupt_descriptor)
		p.interrupt_disable_functions.append(timer0_stop)
		p.interrupt_disable_functions.append(watchdog_stop)
		p.ram.set_x_data_at(19, p.ram.memlib.newIOFuncts(gifr_write, gifr_read))
		p.ram.set_x_data_at(20, p.ram.memlib.newIOFuncts(t0tsr_write, t0tsr_read))
		p.process()
		input("hit enter to exit")
		sys.exit()
