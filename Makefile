CC = gcc
CFLAG = -O -o

CLANG = clang-3.7
CLANGCHECK = clang-check-3.7

PWD = pwd

all:clean libmemory.so

libmemory.so:
	$(CC) -shared -fPIC $(CFLAG) lib/libmemory.so c_src/memory.c &&\
	echo "shared_lib = \"`$(PWD)`/lib/libmemory.so\"" > shared_lib.py &&\
	echo "shared_lib = \"`$(PWD)`/lib/libmemory.so\"" > core/shared_lib.py
clean:
	rm -f lib/libmemory.so||true;\
	rm -f lib/libclangmemory.so||true

clang:
	$(CLANG)  -shared -fPIC $(CFLAG) lib/libclangmemory.so c_src/memory.c &&\
	echo "shared_lib = \"`$(PWD)`/lib/libclangmemory.so\"" > shared_lib.py &&\
	echo "shared_lib = \"`$(PWD)`/lib/libclangmemory.so\"" > core/shared_lib.py

clang-check:
	$(CLANGCHECK) c_src/memory.c -ast-dump --


