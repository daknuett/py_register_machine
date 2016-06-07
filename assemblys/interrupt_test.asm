#include<new_stddef.inc>

; example about interrupts
; using 2 interrupts to show the usage of GIFR
; and T0TSR


; Timer0 Time Set Register
; set timer0 time to 3
ldi 3 T0TSR


; enable timer0
ldi 2  r0

; enable watchdog
addi 1 r0
; r0 = (1 << 0) | ( 1 << 1)
; (1 << 0) is watchdog enable
; (1 << 1) is timer0 enable

; enable interrupts by loading the value to GIFR
; ( = Global Interrupt Flag Register).
; Now the Interrupts will be enabled.
mov r0 GIFR


; wait for interrupts
mainloop:
ldi 's' out1
ldi 't' out1
ldi 'i' out1
ldi 'l' out1
ldi 'l' out1
ldi a out1
jmp mainloop

; just print a little message
foo_interrupt_handle:
ldi 'h' out1
ldi 'a' out1
ldi 'l' out1
ldi 'l' out1
ldi 'o' out1
ldi a out1
ret

; shut down the system
watchdog_handle:
; disable interrupts
ldi 0 r0
mov r0 GIFR
; shut down
ldi ff SFR
ret


@interrupt timer0
; go to our interrupt handle
icall foo_interrupt_handle
; ``ret'' is obsolete, will be added by the assembler.
; a blank interrupt would be:
;     @interrupt timer0
;     ret

@interrupt watchdog
icall watchdog_handle
