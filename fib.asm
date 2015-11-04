fib:
ldi 1 curr
ldi 1 last
mov until until_str
;ldi 73 2
fib.loop:
mov curr swap
mov swap 12
addi 30 12
add last curr
mov swap last
sub until_str swap
mov swap 12
;addi 30 12
;mov 12 2
;mov a 2
jgt swap fib.loop
mov curr 1
;addi 30 curr
;mov curr 2
;mov a 2
ret
