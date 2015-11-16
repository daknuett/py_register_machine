; testing the "lcd like" graphics
; reg 10 is the char to put
; reg 11 is the cursor position

; load a chr in the char register
; cursor is at 0
ldi 'f' a 
; cursor now at 1
inc b
ldi 'o' a
inc b
ldi 'o' a
addi 2 b
ldi 'H' a
inc b
ldi 'i' a
inc b
ldi '!' a

; start tk.mainloop
ldi 06 3

ldi ff 3
