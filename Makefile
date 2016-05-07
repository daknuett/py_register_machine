CC = gcc
CFLAG = -O -o

CLANG = clang-3.7
CLANGCHECK = clang-check-3.7

all:clean libmemory.so

libmemory.so:
	$(CC) -shared -fPIC $(CFLAG) libmemory.so memory.c
clean:
	rm -f libmemory.so||true

clang:
	$(CLANG)  -shared -fPIC $(CFLAG) libclangmemory.so memory.c

clang-check:
	$(CLANGCHECK) memory.c -ast-dump --
