; std definitions for the main register machine
#define r0	0
#define r1	1
#define	r2	2
#define r3	3
#define	r4	4
#define	r5	5
#define	r6	6
#define r7	7
#define r8	8
#define r9	9
#define r10	a
#define r11	b
#define	r12	c
#define r13	d
#define	r14	e
#define	r15	f
#define	r16	10
#define r17	11
#define SFR	12
#define out1	15
; the Global Interrupt Flag Register ( enable interrupts)
#define	GIFR	13
; Timer0 Time Set Register 
#define	T0TSR	14
; currently there is a memory of size 400
#define RAMEND_HIGH 190
; 21 registers
#define RAMEND_LOW 16
