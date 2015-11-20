#include<stddef.inc>
#import<memcpy.asm>
start:
; for jump and exit: set a counter
inc 15

; load myself into ram
; attention: hold some free ram between RAMEND_LOW and me
ldi RAMEND_LOW r1
; 16 blocks space
; this is dest
addi 10 r1
; now src
ldi RAMEND_HIGH r2
; size 
ldi 50 r3
; set the args
ldi RAMEND_LOW r0
movp r2 r0
inc r0
movp r1 r0
inc r0
movp r3 r0
call memcpy

; done
ldi ff SFR
