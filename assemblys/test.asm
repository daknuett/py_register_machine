#import<fib.asm>
#include<fib.inc>
#include<stddef.inc>
ldi 0 r0
start:
ldi 15 until
call fib
mov 1 r0
ldi 04 SFR

ldi ff SFR

