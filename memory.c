
#define SFR_REG	1
#define	OUT_REG	2
#define STD_REG	3


struct _Register;
typedef struct _Register Register;

struct _Register
{
	int value;
	unsigned int name;
	void ( * write)( Register *, int);
	int ( * read )(Register *);
	void * x_data; // xtra data, file FILE streams,...
};

//typedef struct _Register Register;

struct _SFRCommand
{
	unsigned int val;
	unsigned int ( * funct)(void);
};
typedef struct _SFRCommand SFRCommand;
struct _SFRCommandHolder
{
	SFRCommand * com;
	struct _SFRCommandHolder * next;
};


#include<stdlib.h>
#include<string.h>
#include<stdio.h>

void ( * do_exit)(int) =exit;
#include<unistd.h>

Register * newRegister(unsigned int name, void * write, void * read)
{
	Register * reg=calloc(1,sizeof(Register));
	reg->name=name;
	reg->write=write;
	reg->read=read;
	return reg;
}

void delRegister(Register * reg)
{
	free(reg);
}

int OutPutRegister_read(Register * reg)
{
	return reg->value;
}
void OutPutRegister_write(Register * reg,int val)
{
	fputc(val,reg->x_data);
	reg->value=val;
	return;
}

Register * newOutPutRegister(unsigned int name,FILE * stream)
{
	Register * reg=newRegister(name,OutPutRegister_write,OutPutRegister_read);
	reg->x_data=stream;
	return reg;
}
int StdRegister_read(Register * reg)
{
	return reg->value;
}
void StdRegister_write(Register * reg,int val)
{
	reg->value=val;
	return;
}

Register * newStdRegister(unsigned int name)
{
	Register * reg=newRegister(name,StdRegister_write,StdRegister_read);
	return reg;
}
int SpecialFunctionRegister_read(Register * reg)
{
	return reg->value;
}


SFRCommand * newSFRCommand(unsigned int val, unsigned int ( * funct)(void))
{
	SFRCommand * com=malloc(sizeof(SFRCommand));
	com->val=val;
	com->funct=funct;
	return com;
}

struct _SFRCommandHolder * new_SFRCommandHolder(SFRCommand * com, struct _SFRCommandHolder * next)
{
	struct _SFRCommandHolder * h=malloc(sizeof(struct _SFRCommandHolder));
	h->com=com;
	h->next=next;
	return h;
}


struct _SFRCommandHolder * sfr_comms=NULL;

void set_sfr_comms(struct _SFRCommandHolder *  h)
{
	#ifdef DEBUG
	printf("adding ( %zd => %zd => %zd  )\n",h,h->com,h->com->funct);
	#endif
	sfr_comms=h;
}
unsigned int SpecialFunctionRegister_exec(unsigned int val)
{
	struct _SFRCommandHolder * curr=sfr_comms;
	unsigned int ret=-1;
	while (curr!=NULL)
	{
		#ifdef DEBUG
		printf("( %zd => %zd => %zd ) %u ?= %u",curr,curr->com,curr->com->funct,curr->com->val,val);
		#endif
		if(curr->com->val==val)
		{
			#ifdef DEBUG
			printf("\t\tTRUE\n");
			#endif

			ret=curr->com->funct();
			#ifdef DEBUG
			printf("callback done.\n");
			#endif
		}
		#ifdef DEBUG
		else
		{
			printf("\t\tFALSE\n");
		}
		#endif
		curr=curr->next;
	}
	return ret;
}

void SpecialFunctionRegister_write(Register * reg,int val)
{
	reg->value=val;
	reg->value=SpecialFunctionRegister_exec((unsigned int) val);
	return;
}

Register * newSpecialFunctionRegister(unsigned int name)
{
	Register * reg=newRegister(name,SpecialFunctionRegister_write,SpecialFunctionRegister_read);
	return reg;
}


int Register_read(Register * reg)
{
	return reg->read(reg);
}
void Register_write(Register * reg,int val)
{
	reg->write(reg,val);
}

Register ** Registers_from_string(char * string)
{
	size_t size,i=0;
	char * token=strsep(&string,"/");;
	char * str=malloc(sizeof(char)*20);
	sscanf(token,"%zd/",&size);
	Register ** regs=malloc(sizeof(Register * ) * size);
	do
	{
		token=strsep(&string,";");
		int nmbr,type;
		if(sscanf(token,"%u,%u,%s",&nmbr,&type,str)!=3)
		{
			printf("unable to scan 3 objects!\n");
		}
		switch(type)
		{
			case (SFR_REG):
				{
					regs[i]=newSpecialFunctionRegister(nmbr);			
				}break;
			case (OUT_REG):
				{
					regs[i]=newOutPutRegister(nmbr,fopen(str,"w"));
				}break;
			case (STD_REG):
				{
					regs[i]=newStdRegister(nmbr);
				}break;
			default:
				{
					regs[i]=newStdRegister(nmbr);
				}break;
		}
		i++;
	}
	while(i<size);
	free(str);
	return regs;
}

struct _Ram
{
	int * mem;
	size_t memsize; // to avoid SIGSEGV
	Register ** regs;// as usually registers are a part of the ram
	unsigned int regs_count;
};

typedef struct _Ram Ram;

Ram * newRam(size_t size,Register ** regs,unsigned int regs_count)
{
	Ram * r=malloc(sizeof(Ram));
	// init all as 0 AND as the registers are a ``part'' of the ram, 
	// there is no need to alloc space for them.
	r->mem=calloc(size-regs_count,sizeof(int));
	if(r->mem==NULL)
	{
		fprintf(stderr,"FATAL: on calloc : %s  %d: out of mem\n",__FILE__,__LINE__);
		exit(-3);
	}
	r->memsize=size;
	r->regs=regs;
	r->regs_count=regs_count;
	return r;
}

int Ram_read(Ram * ram,size_t iter)
{
	if(iter>=ram->memsize)
	{
		// avoid SIGSEGV
		iter=ram->memsize-1;
	}
	if(iter < ram->regs_count)
	{
		return Register_read(ram->regs[iter]);
	}
	iter-=ram->regs_count;
	return ram->mem[iter];
}

void Ram_write(Ram * ram,size_t iter,int val)
{
	if(iter>=ram->memsize)
	{
		// avoid SIGSEGV
		iter=ram->memsize-1;
	}
	if(iter < ram->regs_count)
	{
		Register_write(ram->regs[iter],val);
		return;
	}
	iter-=ram->regs_count;
	ram->mem[iter]=val;	
}

/*
   Dump the ram to a file specified by ``filename'',
   using char * filename for better Python3 compability.
 */
void Ram_dump(Ram * ram,char * fname) 
{
	FILE * fout=fopen(fname,"w");
	/* using the predefined functions might slow this a bit,
	   but I think, that this can be ignored */
	size_t i;
	for(i=0;i<ram->memsize;i++)
	{
		fprintf(fout,"%zx\t%x\n",i,Ram_read(ram,i));
	}
	fclose(fout);
	return;
}
struct _Flash;
typedef struct _Flash Flash;

struct _Flash
{
	size_t size;
	int * mem;
};

Flash * newFlash(size_t size)
{
	Flash * f= malloc(sizeof(Flash));
	f->mem=calloc(size,sizeof(int));
	if(f->mem==NULL)
	{
		fprintf(stderr,"ERROR: out of mem: in calloc: %s: %d",__FILE__,__LINE__);
		exit(-3);
	}
	f->size=size;
	return f;
}

void Flash_dump(Flash * flash,char * fname)
{
	FILE * fout=fopen(fname,"w");
	size_t i;
	fprintf(fout,"%zd\n",flash->size);
	for(i=0;i<flash->size;i++)
	{
		fprintf(fout,"%zx\t%x\n",i,flash->mem[i]);
	}
	fclose(fout);
	return;
}

void Flash_write(Flash * flash,size_t iter,int val)
{
	if(flash->size <= iter)
	{
		iter=flash->size-1;
	}
	flash->mem[iter]=val;
	return;
}

int Flash_read(Flash * flash, size_t iter)
{
	if(flash->size <= iter)
	{
		iter=flash->size-1;
	}
	return flash->mem[iter];
}

Flash * Flash_from_file(char * fname)
{
	FILE * fin=fopen(fname,"r");
	if(fin==NULL)
	{
		fprintf(stderr,"ERROR: %s %u: file not found :%s\n",__FILE__,__LINE__,fname);
		exit(-2);
	}
	size_t size,null,i;
	// reading unsigned as '%x' does not support +/-
	unsigned int val;
	null=fscanf(fin,"%zd\n",&size);
	printf("reading size: %zd\n",size);
	Flash * f= malloc(sizeof(Flash));
	f->mem=calloc(size,sizeof(unsigned int));
	if(f->mem==NULL)
	{
		fprintf(stderr,"ERROR: out of mem: in calloc: %s: %d",__FILE__,__LINE__);
		exit(-3);
	}
	for(i=0;i<size;i++)
	{
		null=fscanf(fin,"%zx\t%x\n",&null,&val);
		f->mem[i]=val;
	}
	f->size=size;
	return f;
}


