#include<stddef.inc>

; defining a memcpy function
; reserved ram: 
; RAMEND_LOW ptr src
; RAMEND_LOW + 1 ptr dest
; RAMEND_LOW + 2 size

memcpy:
; save the registers
push r0
push r1
push r2
push r3
push r4
push r5
push r6
; move args to registers
ldi RAMEND_LOW r2
pmov r2 r0
inc r2
pmov r2 r1
inc r2
pmov r2 r3
; relocating args done
; now: copy the content
; most efficient way: high to low
; calculate the endpoint
mov r3 r4
add r0 r3
add r1 r4
memcpy_loop:
; need a register as swap
pmov r3 r5
movp r5 r4
; copy done
dec r3
dec r4
; check, if we are done
mov r0 r5
sub r3 r5
jge r5 memcpy_loop
; and we are done!!

pop r0
pop r1
pop r2
pop r3
pop r4
pop r5
pop r6
ret

