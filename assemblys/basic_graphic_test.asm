#include<stddef.inc>
; testing the "lcd like" graphics
; reg 10 is the char to put
; reg 11 is the cursor position

; load a chr in the char register
; cursor is at 0

ldi mystr r0
call putstr
inc LCD_cur
; start tk.mainloop
ldi 06 SFR

putstr:
push r1
putstr_loop:
pmov r0 r1
mov r1 LCD_chr
inc LCD_cur
inc r0
jne r1 putstr_loop
pop r1
ret


.string mystr "Hi, this is py register machine. "


