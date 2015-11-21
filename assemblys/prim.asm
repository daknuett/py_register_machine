; berechnen, ob zahl primzahl ist

#include<stddef.inc>

start:
; berechne 19
ldi 13 RAMEND_LOW
call prim
ldi ff SFR

prim:
mov RAMEND_LOW r1
ldi 2 r0
prim_loop:
mov r0 r2
mod r1 r2
jeq r2 is_prim
mov r1 r2
mul r2 r2
sub r0 r2
jge r2 not_prim
inc r0
jmp prim_loop

is_prim:
ldi 'T' out1
ldi a out1
mov r1 r0
ldi 4 SFR
ret

not_prim:
ldi 'F' out1
ldi a out1
mov r1 r0
ldi 4 SFR
ret

