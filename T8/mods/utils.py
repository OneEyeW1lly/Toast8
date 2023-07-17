from enum import Enum
import sys, os

# UTILS
def clear_screen():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')

# EMUMS
class Instruction(Enum):
	i_nop = 0
	i_mw = 1
	i_lw = 2
	i_sw = 3
	i_push = 4
	i_pop = 5
	i_lda = 6
	i_jnz = 7
	i_inb = 8
	i_outb = 9
	i_add = 10
	i_adc = 11
	i_and = 12
	i_or = 13
	i_nor = 14
	i_sbb = 15
	i_hlt = 16

class Register(Enum):
	r_a = 0
	r_b = 1
	r_c = 2
	r_d = 3
	r_l = 4
	r_h = 5
	r_z = 6
	r_f = 7

class Special(Enum):
	sp_mb = 0
	sp_sp = 1
	sp_pc = 2

class Flag(Enum):
	f_less = 0
	f_equal = 1
	f_carry = 3
	f_borrow = 4

class Port(Enum):
	p_status = 0

class Status(Enum):
	s_unused0 = 0
	s_error = 1
	s_unused1 = 2
	s_halt = 3

# CLASSES
class File:
	def __init__(self, path:str):
		self.path = path
		self.global_type = str()

	def read(self) -> any:
		return None

	def write(self, data) -> None:
		pass

	def t_read(self, tp:str, index:int=None, length:int=None) -> any:
		ret = None
		with open(self.path, tp) as fpr:
			if index:
				fpr.peek(index)
			else:
				pass

			if length:
				ret = fpr.read(length)
			else:
				ret = fpr.read()
		return ret


	def t_write(self, data:any, tp:str, index:int=None) -> None:
		with open(self.path, tp) as fpw:
			if index:
				fpw.peek(index)

			fpw.write(data)
















