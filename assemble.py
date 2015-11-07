from assembler import *
from processor import *
from memory import *

from optparse import OptionParser
import os,sys

"""
assemble a file and store the flash.
"""


if __name__=="__main__":
	parser=OptionParser()
	parser.add_option("-f","--file",action="store",type="str",dest="fname",help="filename to assemble")
	parser.add_option("-o","--out",action="store",type="str",dest="out_file",default="a.flash",help=" name of the output file")
	parser.add_option("-v","--verbose",action="store_true",dest="verbose",default=False,help="more output")
	parser.add_option("-p","--processor-def",action="store",type="str",dest="proc_def",help="name of the file with your processor definition")

	(opts,args)=parser.parse_args()

	DEBUG=opts.verbose
	if(opts.fname==None):
		print("need -f try -h")
		sys.exit(1)
	if(opts.proc_def==None):
		print("need -p try -h")
		sys.exit(1)
	p=Preprocessor(opts.fname)
	p.do_all()
	proc=Processor.from_str(open(opts.proc_def).read())
	asm=Assembler(proc,opts.fname+".pr")
	asm.compile()
	proc.flash.dump(opts.out_file)
	os.system("rm -f "+opts.fname+"\.pr*")	
