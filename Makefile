CC=gcc
CFLAG=-O -o

all:clean libmemory.so

libmemory.so:
	$(CC) -shared -fPIC $(CFLAG) libmemory.so memory.c
clean:
	rm -f libmemory.so||true
