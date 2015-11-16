; testing the "lcd like" graphics
; reg 10 is the char to put
; reg 11 is the cursor position

; load a chr in the char register
; cursor is at 0
; f
ldi 66 a 
; cursor now at 1
inc b
; o
ldi 6f a
inc b
ldi 6f a
; done.

; start tk.mainloop
ldi 06 3

ldi ff 3
