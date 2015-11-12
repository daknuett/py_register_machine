#import"fib.asm"
#import"pr_int.asm"
#include"fib.inc"
ldi a 2
ldi 0 0
start:
ldi 15 until
call fib
mov 1 0
call print_int
ldi a 2
ldi 05 0
ldi 04 3

; pointer !
ldi 50 4
movp 0 4
ldi 3 0
pmov 4 0
ldi 04 3
; at&t style
mov 0 (4)
ldi 3 0
mov (4) 0
ldi 04 3

ldi ff 3

