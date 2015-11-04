; print an integer value to the 
; outputregister at mem<2>
; NOTE: the value is inverted!!
; -> 25 -> output -> 52
print_int:
; number is in 0
mov 0 12
ldi 30 10
ldi a 11
mov 11 1
print_int_loop:
mov 12 0
mov 11 1
mod 0 1
add 10 1
mov 1 2
mul 11 11
mov 11 1
ldi a 4
div 0 4
mov 4 12
subi 30d40 1
jgt 1 print_int_loop
ret
