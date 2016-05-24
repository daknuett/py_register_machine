#import<fib.asm>
#include<fib.inc>
#include<stddef.inc>
start:
mov test_byte until
call fib
mov 1 r0
ldi 04 SFR

mov r0 1d4
fdump

ldi ff SFR

.set test_byte 15
