fib:
push 1
push 0
push 2
push 4
push 5
ldi 1 curr
ldi 1 last
mov until until_str
fib.loop:
mov curr swap
add last curr
mov swap last
sub until_str swap
jgt swap fib.loop
mov curr 1
pop 2
pop 0
pop 4
pop 5
ret
