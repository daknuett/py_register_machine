/* startfunktion */
function void start()
	int f=45;
	int b=foo(f);
	HW_PR(b)
	halt();

function int foo(int arg1)
	int bar=10;
	if(arg1>5)
		bar += arg1;
	else
		bar -= arg1;
	int i=0
	while(i<(bar/2))
		bar += i;
	return bar;


function void HW_PR(int arg)
	/* inline assembler muss wegen hardware access sein */
	__ASM__("mov arg r0");
	__ASM__("ldi 03 SFR");

function void halt()
	__ASM__("ldi ff SFR");
