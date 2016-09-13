# py_register_machine
a register machine written in python3

___WARNING___:

__PyRegisterMachine is deprecated and no longer supported. Use PyRegisterMachine2 instead!__

[PyRegisterMachine2](https://github.com/daknuett/py_register_machine2)
[PyRegisterMachine2 docs](https://daknuett.github.io/py_register_machine2)


You can write programs for the machine using the KASM assembly language.
Compile it using the assembler.py package.

(C) 2015 Daniel Knuettel

See the ___GNU AGPL V3___ for further Information about copyright and warranty,
as there ___IS NO WARRANTY PERMITTED BY THE AUTHOR___.

The complete engine is as extensible as possible,
so adding more features should be easy.


___NOTE___: it is important, to use the assembler with the correct
processor definitions, the result would be unpredictable, if you won't.

___NOTE___: the programm is usually executed directly from the flash drive,
but you also can load it into the ram. In addition to this,
Flash, Ram and registers are handled completly the same way: you can make
memory operations __without__ using a register! (but it is not really recommended.)

___NOTE___: usually the only symbolic names are jump marks.
You can specify register names in an _.inc_ file and 
include them using the __#include__ statement.  
( use `#include<new_stddef.inc>` for some definitions )

Predefined routines can be included using the __#import__ statement.
This means, that no linking and/or memory rearrangement is supported,
but you are _welcome_ to add a better compiler/assembler/linker.
The commands  __st__ or __ld__ are not yet implemented.

The engine is not designed for a fix usage, but for expansion 
_from the user_, so no assembly directive/mnemonic definition is provided,
as _everybody_ may add his very own directives and mnemonics. 

## Installation

* in-a-folder   
 * Make the directory you want to work in using `mkdir -p /home/<you>/path/to/folder`
 * Go to that directory `cd /home/<you>/path/to/folder`
 * Get the source using `git clone https://github.com/daknuett/py_register_machine --single-branch -b current`
 
* under the $PYTHONPATH
 * Go to a path in $PYTHONPATH `cd /home/<you>/.local/lib/python3.5/site-packages/
 * Get the source using `git clone https://github.com/daknuett/py_register_machine --single-branch -b current`

## Usage
__Run a sample__

* in-a-folder
 * Go to your directory `cd /home/<you>/path/to/folder`
 * Assemle the sample: `python3 -m py_register_machine.assemle -f py_register_machine/assemblys/interrupt_test.asm -p py_register_machine/procdefs/new_processor.def`
 * Run the sample: `python3 -m py_register_machine.main a.flash py_register_machine/procdefs/new_processor.def`

* under $PYTHONPATH
 * Go to any directory
 * Get the Sample and a processor definition:
  * `cp /home/<you>/.local/lib/python3.5/site-packages/py_register_machine/assemblys/interrupt_test.asm ./`
  * `cp /home/<you>/.local/lib/python3.5/site-packages/py_register_machine/procdefs/new_processor.def ./`
 * Assemble: `python3 -m py_register_machine.assemle -f interrupt_test.asm -p new_processor.def`
 * Run: `python3 -m py_register_machine.main a.flash new_processor.def`



___See___ the project's wiki < https://github.com/daknuett/py_register_machine/wiki > page for more info about usage.

___See___ also the tutorial/documentation project < https://github.com/daknuett/py_register_machine_tutorials > for further interesting infos

### Plans

* Use more pythonic definitions for Register Machines
* Generate a more module-conformable interface
* A complete rewrite with a slightly modified architecture, removing all the bad debts

_Daniel Knuettel_
