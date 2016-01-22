#!/usr/bin/python3

import sys

from memory import *
from processor import *
use_gui = True
if( use_gui):
	try:
		from basic_graph import *
	except:
		print("warning: lcd alike graphics disables (no python3-tk found)")
		print("install python3-tk or set ``main.use_gui = False'' to disable this warning")
		use_gui = False

# a complete ready to use register machine
# 

if __name__=="__main__":
	r=Ram(400,registers="12/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;11,4,n;",register_count=12)
	if(len(sys.argv)<=2):
		print("usage: {} <command> <argument>".format(sys.argv[0]))
		raise BaseException("need command")
	if(sys.argv[1]=="procdef"):
		f=Flash(1000)
		p=Processor(ram=r,flash=f)
		p.__dump__(sys.argv[2])
		print("generated processor definition into file {}.".format(sys.argv[2]))
		sys.exit()
	if(sys.argv[1]=="execute"):
		fname=sys.argv[2]
		fil=open(fname,"r")
		flash_size=int(fil.readline())
		fil.close()
		f=Flash(flash_size,std_savename=fname.encode(),saved=True)
		p=Processor(ram=r,flash=f)
		if(use_gui):
			g=BasicGraphics(r,10,11)
		p.process()
		input("hit enter to exit")
		sys.exit()
	print("command {} not recognized".format(sys.argv[1]))
