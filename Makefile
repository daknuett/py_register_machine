CC=gcc
CFLAG=-O -o


libmemory.so:
	$(CC) -shared -fPIC $(CFLAG) libmemory.so memory.c
