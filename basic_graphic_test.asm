#include<stddef.inc>
; testing the "lcd like" graphics
; reg 10 is the char to put
; reg 11 is the cursor position

; load a chr in the char register
; cursor is at 0
ldi 'f' LCD_chr 
; cursor now at 1
inc LCD_cur
ldi 'o' LCD_chr
inc LCD_cur
ldi 'o' LCD_chr
addi 2 LCD_cur
ldi 'H' LCD_chr
inc LCD_cur
ldi 'i' LCD_chr
inc LCD_cur
ldi '!' LCD_chr

; start tk.mainloop
ldi 06 SFR

ldi ff SFR
