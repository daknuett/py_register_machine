from .processor import *
from threading import Timer
from .memory import *

watchdog_en = [False]
__watchdog_callable = [None]
__current_watchdog_timer = None

def watchdog_start(_callable):
	__watchdog_callable[0] = _callable
	if(not watchdog_en[0]):
		return
	__current_watchdog_timer = Timer(4, watchdog_interrupt)
	__current_watchdog_timer.start()

def watchdog_interrupt():
	if(__watchdog_callable[0]):
		__watchdog_callable[0]()
	__current_watchdog_timer = Timer(4, watchdog_interrupt)
	__current_watchdog_timer.start()
	

def watchdog_reset():
	if(__current_watchdog_timer):
		__current_watchdog_timer._delete()
		__current_watchdog_timer = Timer(4, watchdog_interrupt)
		t.start()
def watchdog_stop():
	if(__current_watchdog_timer):
		__current_watchdog_timer._delete()

def get_watchdog_callable():
	return __watchdog_callable[0]

watchdog_interrupt_descriptor = InterruptDescriptor("watchdog", watchdog_start)

timer0_en = [False]
timer0_time = [0]
__timer0_timer = None
__timer0_callable = [None]


def timer0_start(_callable):
	print("DEBUG:: timer0_start:: ({}|{}|{})".format(timer0_en[0], timer0_time[0], _callable))
	__timer0_callable[0] = _callable
	if(not timer0_en[0]):
		return
	__timer0_timer = Timer(timer0_time[0], timer0_interrupt)
	__timer0_timer.start()

def timer0_interrupt():
	if(__timer0_callable[0]):
		__watchdog_callable[0]()
	__timer0_timer = Timer(timer0_time[0], timer0_interrupt)
	__timer0_timer.start()
def timer0_stop():
	if(__timer0_timer):
		__timer0_timer._delete()
def get_timer0_callable():
	return __timer0_callable[0]

timer0_interrupt_descriptor = InterruptDescriptor("timer0", timer0_start)


__GIFR = 0

interrupt_bits = { 0x01: (watchdog_en, watchdog_start, watchdog_stop, get_watchdog_callable ),
		0x02: (timer0_en, timer0_start, timer0_stop, get_timer0_callable)}

stuff_to_store = []

def en_dis_interrupts(reg, content):
	__GIFR = content
	for bit, interrupt_stuff in interrupt_bits.items():
		enable, start, stop, get_callable = interrupt_stuff
		if(content & bit):
			enable[0] = True
			start(get_callable())
		else:
			enable[0] = False
			stop()
	return 0
def gifr_content(*args):
	return __GIFR

gifr_write = IO_FUNCT_WRITE(en_dis_interrupts)
gifr_read = IO_FUNCT_READ(gifr_content)
stuff_to_store.append((gifr_write,gifr_read))

def timer0_set_time(reg, time):
	timer0_time[0] = time
	return 0
def timer0_get_time(reg):
	return timer0_time[0]

t0tsr_write = IO_FUNCT_WRITE(timer0_set_time)
t0tsr_read = IO_FUNCT_READ(timer0_get_time)

stuff_to_store.append((t0tsr_write,t0tsr_read))

