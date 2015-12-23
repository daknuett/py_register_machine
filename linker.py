from linkableAssembler import *
from memory import *
from processor import *


class Linker(object):

	def __init__(self,objects,processor,static_symbols,startname="start",data_sec_name="_data",debug=0):
		self.objects=objects
		self.processor=processor

		self.debug=debug

		self.data_sec_name=data_sec_name
		self.startname=startname

		self.static_symbols=static_symbols
		# we need some commands ( like call) so setup the inversed commands:
		self.commands = {v:k for k,v in self.processor.tb_commands.items()}
		self.commands.update({v:k for k,v in self.processor.db_commands.items()})
		self.commands.update({v:k for k,v in self.processor.sg_commands.items()})
		
		self.refactored_objects={}

	def check_for_relocatables(self):
		""" move through the objects and check for called objects.
			called objects can be relocated.
			"""
		call = None
		try:
			call = self.commands["call"]
		except KeyError:
			# no relocatable blocks. ( maybe datasection)
			refactored_objects={}
			for block_def,block in self.objects:
				if(block_def[1] == self.data_sec_name):
					refactored_objects[(block_def[0],block_def[1],block_def[2],block_def[3],True)]=block
				elif(blockdef[1] == self.startname):
					refactored_objects[(block_def[0],block_def[1],block_def[2],block_def[3],True)]=block
				else:
					refactored_objects[(block_def[0],block_def[1],block_def[2],block_def[3],False)]=block
			return
				

		# at first search all call s
		call_blocknos = []

		called_objects = []

		for object_def,block in self.objects.items():
			# search the calls
			if(block == call):
				call_blocknos.append(object_def)
		for startname,currentblock,blockno,prev in call_blocknos:
			if self.debug > 3:
				print("found called block: '{}' in block {}".format(
					self.objects[startname,currentblock,blockno+1,prev],blockno+1))
			called_objects.append(self.objects[startname,currentblock,blockno+1,prev])
		# ok all called  blocks are found

		# refactor the objects:

		for block_def,block in self.objects.items():
			startname,objectname,blockno,prev=block_def
			if(objectname in called_objects or objectname == self.data_sec_name or objectname == self.startname):
				self.refactored_objects[startname,objectname,blockno,prev,True]=block
			else:
				self.refactored_objects[startname,objectname,blockno,prev,False]=block
	def get_object_by_name(self,name):
		unordered=[]
		for k,v in self.objects.items():
			if(k[1] == name):
				if(self.debug > 9 ):
					print(" get_object_by_name: found ",k)
				unordered.append((k,v))
		ordered = sorted(unordered,key=lambda x: x[0][2])
		res = [ i[-1] for i in ordered]
		return res
	def get_full_object_by_name(self,name):
		unordered=[]
		for k,v in self.objects.items():
			if(k[1] == name):
				unordered.append((k,v))
		ordered = sorted(unordered,key=lambda x: x[0][2])
		return ordered
	def get_full_object_by_parent(self,parentname):
		unordered=[]
		for k,v in self.objects.items():
			if(k[3] == parentname and k[1] != parentname):
				if(self.debug > 9 ):
					print(" get_object_by_parent: found ",k)
				unordered.append((k,v))
		ordered = sorted(unordered,key=lambda x: x[0][2])
		return ordered
	def get_object_by_parent(self,parentname):
		return [ i[-1] for i in self.get_full_object_by_parent(parentname) ]

	def relocate_objects(self):
		complete=[]
		start = self.get_object_by_name(self.startname)
		complete.extend(start)
		if(self.debug>3):
			print("start seq: ",complete)
		currentname=self.startname
		while(1):
			current_obj = self.get_full_object_by_parent(currentname)
			if(self.debug > 3):
				print("inserting name {} : {} ".format(currentname,current_obj))
			if(current_obj == []):
				break;
			complete.extend(self.get_object_by_parent(currentname))
			currentname = current_obj[0][0][1]
		complete.extend(self.get_object_by_name(self.data_sec_name))
		if(self.debug>3):
			print(complete)
		return complete
	def insert_references(self,unlinked):
		linked=[]
		block=0
		for u in unlinked:
			if(isinstance(u,int)):
				linked.append(u)
			elif(u in self.static_symbols):
				linked.append(self.static_symbols[u])
			elif( self.get_object_by_name(u) != [] ):
				if(self.get_full_object_by_name(u)[0][0][3] != self.data_sec_name):
					# and again: diff between tb_commands and db_commands
					# XXX WARNING: this way is unsafe!! I will change this ( hopefully ). FIXME
					# TODO MAKE THIS BETTER
					# FIXME and this hardcoded tb_cmd_jumpers is bad!!!!
					db_cmd_jumpers=[self.commands["call"],self.commands["jmp"]]
					tb_cmd_jumpers=[self.commands["jne"],self.commands["jeq"],self.commands["jge"],self.commands["jgt"],self.commands["jle"],self.commands["jlt"]]
					if(unlinked[block-1] in db_cmd_jumpers):
						if(self.debug>0):
							print("FIXME: assuming to be called by a db_command, adding 1")

						if(self.debug>2):
							print("block {} : adding reference to {}".format(u,(self.get_full_object_by_name(u)[0][0][2]-block)+1))
						linked.append((self.get_full_object_by_name(u)[0][0][2]-block)+1)
					if(unlinked[block-2] in tb_cmd_jumpers):
						if(self.debug>0):
							print("FIXME: assuming to be called by a tb_command, adding 2")

						if(self.debug>2):
							print("block {} : adding reference to {}".format(u,(self.get_full_object_by_name(u)[0][0][2]-block)+2))
						linked.append((self.get_full_object_by_name(u)[0][0][2]-block)+2)

				else:
					if(self.debug>2):
						print("block {} : adding reference to {}".format(u,(self.get_full_object_by_name(u)[0][0][2])))
					linked.append((self.get_full_object_by_name(u)[0][0][2]))
			else:
				raise UnboundReferenceError("no reference to {}.".format(u))
			block += 1
		return linked
	def link(self):
		self.check_for_relocatables()
		unlinked=self.relocate_objects()
		linked=self.insert_references(unlinked)
		return linked
	def program_flash(self):
		content=self.link()
		pointer=0
		for block in content:
			self.processor.flash.write(pointer,block)
			pointer += 1



if __name__=="__main__":
	r=Ram(400,registers="12/0,3,n;1,3,n;2,2,/dev/stdout;3,1,n;4,3,n;5,3,n;6,3,n;7,3,n;8,3,n;9,3,n;10,4,n;11,4,n;",register_count=12)
	f=Flash(1000)
	p=Processor(ram=r,flash=f)
		
	l=LinkableAssembler(p,"assemblys/prim.asm","start",debug=5)
	i,symbs,le=l.compile()

	linker = Linker(i,p,symbs,debug=6)
	linker.program_flash()

	f.dump("linked.flash")	
#	p.process()
