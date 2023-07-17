import struct
import ctypes
from mods.utils import *

# CLASSES
class mem:
	def __init__(self, size:int=0xFFFF) -> None:
		self.raw = [0]*size
		self.WriteProtect = False

	def peek(self, addr:int) -> int:
		return self.raw[addr]

	def poke(self, addr:int, data:int) -> None:
		self.raw[addr] = data

class register:
	def __init__(self, name:str) -> None:
		self.value = 0
		self.name = name

	def get(self) -> int:
		return self.value

	def set(self, data:int) -> None:
		self.value = data 

	def inc(self, val:int=1) -> int:
		return self.value += val

	def dec(self, val:int=1) -> int:
		return self.value -= val

class T8:
	def __init__(self) -> None:
		self.status:int = 0
		self.is_simulating = False

		# mem
		self.mem:object = mem()
		self.mem.WriteProtect = True

		# reg
		self.reg_a:object = register("A")
		self.reg_b:object = register("B")
		self.reg_c:object = register("C")
		self.reg_d:object = register("D")
		self.reg_l:object = register("L")
		self.reg_h:object = register("H")
		self.reg_z:object = register("Z")
		self.reg_f:object = register("F")
		
		self.registers:list = [self.reg_a, self.reg_b, self.reg_c, self.reg_d, self.reg_l, self.reg_h, self.reg_z, self.reg_f]
		self.HL:object = register("HL")

		# special
		self.spec_mb:int = 0
		self.spec_sp:int = 0
		self.spec_pc:int = 0
		self.specials:list = [self.spec_mb, self.spec_sp, self.spec_pc]

	def halted(self) -> bool:
		if (self.status == Status.s_halt): return True
		return False

	def ParseInstruction(self, byte_code:bytes): 
		# XXXXYZHHHHLLL
		# X: 4-bit instructions id
		# Y: false(0) if arg1 = imm(8/16) ; true(1) if arg1 = register
		# Z: false(0) if arg2 = imm(8/16) ; true(1) if arg2 = register
		# H: 4-bit reg1 id OR imm(8/16) val
		# L: 4-bit reg2 id OR imm(8/16) val
		
		unpacked:tuple = struct.unpack("<i??ii", byte_code)
		print(f"byte_code: {byte_code}\nunpacked: {unpacked}")
		return {
			"inst": unpacked[0],
			"is_reg_1": unpacked[1],
			"is_reg_2": unpacked[2],
			"high_data": unpacked[3],
			"low_data": unpacked[4]
		}
	
	def step(self) -> int:
		if (self.halted()): return 1
		print(f"\nPC: {self.spec_pc}")	
		instruction = self.mem.peek(self.spec_pc)
		pinst = self.ParseInstruction(instruction.to_bytes(struct.calcsize("<i?ii"), "little")) 
		inst = pinst['inst']
		is_reg_1 = pinst['is_reg_1']
		is_reg_2 = pinst['is_reg_2']
		high_data = pinst['high_data']
		low_data = pinst['low_data']

		#instruction_id, is_reg, args = self.ParseInstruction(inst.to_bytes(struct.calcsize("<i?ii"), "little")) 
		print(f"instruction_id: {instruction_id}\nis_reg: {is_reg}\narguments: {args}")
		if (instruction_id == Instruction.i_mw.value):	
			if (is_reg):
				#self.spec_pc += 1
				#print(self.spec_pc)
				#print(self.registers[self.mem.peek(self.spec_pc)].get())
				self.registers[high_data].set(self.registers[low_data].get()) 
				#print(self.registers[reg_id].get())
			else:	
				#self.spec_pc += 1
				self.registers[high_data].set(self.mem.peek(low_data))

		elif (instruction_id == Instruction.i_lw.value):
			if (is_reg):
				self.registers[high_data].set(self.registers[low_data].get())
			else:
				#self.spec_pc += 1
				#self.spec_pc.set(self.spec_pc.get()+1)
				
				#print(f"{self.registers[high_data].name} <- {self.mem.peek(low_data)} : self.registers[{high_data}].name <- {low_data}")
				self.registers[high_data].set(low_data)	

		elif (instruction_id == Instruction.i_sw.value):
			if (is_reg):
				self.registers[low_data].set(self.registers[low_data].get())
			else:	
				#self.spec_pc += 1	
				#self.spec_pc.set(self.spec_pc.get()+1)
				self.mem.poke(self.mem.peek(high_data), self.registers[low_data].get())		

		elif (instruction_id == Instruction.i_push.value):
			self.spec_sp -= 1 
			
			if (is_reg):
				self.mem.poke(self.spec_sp.get(), self.registers[high_data].get())				
			else:
				#self.spec_pc += 1
				#self.spec_pc.set(self.spec_pc.get()+1)
				self.mem.poke(self.spec_sp, self.mem.peek(high_data))

		elif (instruction_id == Instruction.i_pop.value):
			if (is_reg):
				self.registers[high_data].set(self.mem.peek(self.spec_sp.get()))
			else: pass

		elif (instruction_id == Instruction.i_lda.value):
			#self.spec_pc += 1
			#self.spec_pc.set(self.spec_pc.get()+1)
			self.HL.set(self.mem.peek(high_data))		

		elif (instruction_id == Instruction.i_jnz.value):
			if (is_reg):
				if (self.registers[high_data].get() != 0):
					self.spec_pc.set(self.HL.get())
			else:
				#self.spec_pc += 1
				#self.spec_pc.set(self.spec_pc.get()+1)
				if (self.mem.peek(high_data) != 0):
					self.spec_pc.set(self.HL.get())

		elif (instruction_id == Instruction.i_inb.value):
			pass

		elif (instruction_id == Instruction.i_outb.value):
			pass

		elif (instruction_id == Instruction.i_add.value):
			pass
				
		elif (instruction_id == Instruction.i_nop.value):
			pass
		elif (instruction_id == Instruction.i_hlt.value):
			self.status = Status.s_halt
		else: 
			pass
		
		
		self.spec_pc += 1
		return None


def run(file_path:str) -> int:
	if not (os.path.exists(file_path)):
		print(f"file: \"{file_path}\" does not exists or could not be located!")
		return 1


	state:object = T8()	

	# USER CODE GOES HERE

	# LW B, 0xFF;
	#state.mem.poke(0, int.from_bytes(struct.pack("<i?ii", Instruction.i_lw.value, False, Register.r_b.value, 0xFF), "little"))
	# MW A, B;
	#state.mem.poke(1, int.from_bytes(struct.pack("<i?ii", Instruction.i_mw.value, True, Register.r_a.value, Register.r_b.value), "little"))
	# HLT
	#state.mem.poke(2, int.from_bytes(struct.pack("<i?ii", Instruction.i_hlt.value, False, 0, 0), "little"))

	# start at beginning	
	state.spec_pc = 0
	
	while (state.halted() != True):
		state.step()
		
		# DEBUG PRINT
		print(f"mem[{state.spec_pc-1}] = {hex(state.mem.peek(state.spec_pc-1))}")
		for i in range(len(state.registers)):
			print(f"REG ({state.registers[i].name}): {state.registers[i].get()}")

	return 0


def main(argv:list, argc:int) -> int:
	inputs = [
		{"name": "help", "desc": "Print all commands and functions"},
		{"name": "run", "desc": "Runs a compiled t8 program (.tx) in the emulator"},
		{"name": "clear", "desc": "Clears the console screen"},
		{"name": "quit", "desc": "Quit/Exit."},
	]
	running:bool = True
	
	while (running == True):
		inp = input(">").lstrip(' ').rstrip(' ').lower().split(' ')	
		if (inp[0] == "help"):
			print("\n == COMMANDS == ")
			for i in inputs:
				print(f"\t{i['name']}: {i['desc']}")	
			print()
		elif (inp[0] == "run"):
			file_p:str = inp[1]
			r:int = run(file_p)
			return r			

		elif (inp[0] == "quit"):
			running = False
		
		elif (inp[0] == "clear"):
			clear_screen()
		
		elif (inp[0] == ""):
			pass
		
		else:
			print(f"\"{inp}\" is not a command!")

	return 0



if __name__ == '__main__':
	r:int = main(sys.argv, len(sys.argv))
	print("Program exited with code: " + str(r)) 






