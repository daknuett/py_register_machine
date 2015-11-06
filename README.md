# py_register_machine
a register machine written in c and python3

You can write programs for the machine using some kind of assembly language.
Compile it using the assembler.py package.

(C) 2015 Daniel Knuettel

See the ___GNU AGPL V3___ for further Information about copyright and warranty,
as there ___IS NO WARRANTY PERMITTED BY THE AUTHOR___.

The complete engine is as extensible as possible,
so adding more features should be easy.

You can test the engine using `python3 assembler.py`.
It will calculate some fibonacci numbers and print one to _/dev/stdout_.
You may take a look at _processor.py_, there you can see how easy it is
to generate an own modified machine. 

___NOTE___: it is important, to use the assembler with the correct
processor definitions, the result would be unpredictable, if you won't.

___NOTE___: the programm is usually executed directly from the flash drive,
but you also can load it into the ram. In addition to this,
Flash, Ram and registers are handled completly the same way: you can make
memory operations __without__ using a register! (but it is not really recommended.)

___NOTE___: usually the only symbolic names, that are used specify a part
of the program. You can specify register names in an _.inc_ file and 
include them using the __#include__ statement.

Predefined routines can be included using the __#import__ statement.
This means, that no linking and/or memory rearrangement is supported,
but you are _welcome_ to add a better compiler/assembler/linker.
The commands __push__ or __st__ or __ld__ are not yet implemented.

The engine is not designed for a fix usage, but for expansion 
_from the user_, so no assembly directive definition is made,
as _everybody_ may add his very own directives. 

___See___ the project's wikii < https://github.com/daknuett/py_register_machine/wiki > page for more info about usage.

_Daniel Knuettel_
