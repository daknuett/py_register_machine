#include<stddef.inc>

start:
ldi test_str r0
call putstr
ldi ff SFR

putstr:
push r1
putstr_loop:
pmov r0 r1
mov r1 out1
inc r0
jne r1 putstr_loop
pop r1
ret




.string test_str "foo bar bla bal"
