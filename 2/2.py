

class int_code:
        
    def __init__(self, mem):
        
        self._debug = True

        # State
        self._memory = mem
        self._pc = 0
        self._halted = False

        # Fetch
        self._curinstr = None

        # Decode
        self._opcode = None
        self._src1 = None
        self._src1val = None
        self._src2 = None
        self._src2val = None
        self._dst1 = None
        
        # Execute
        self.res = None

        # Writeback

    def reset(self, mem):
        
        self._memory = mem
        self._pc = 0
        self._halted = False

        self._curinstr = None
        self._opcode = None
        self._src1 = None
        self._src1val = None
        self._src2 = None
        self._src2val = None
        self._dst1 = None
        self._res = None

    def fetch_instruction(self):
        assert(self._pc < len(self._memory))

        opcode = self._memory[self._pc]
        
        # Instr of the form INST SRC1 SRC2 DST1
        if opcode in [1, 2]:
            assert(self._pc + 3 < len(self._memory))
            self._curinstr = self._memory[self._pc:self._pc+4]
            self._pc = self._pc + 4 # Consume 4B

        # Instr of the form INST
        elif opcode in [99]:
            self._curinstr = [self._memory[self._pc]]
            self._pc = self._pc + 1 # Consume 1B
        else:
            self._halted = True
            print("Encountered unknown opcode! {0}".format(opcode))


    def decode_instruction(self):
        
        if self._debug:
            self.print_cur_instr()

        assert(len(self._curinstr) > 0)

        opcode = self._curinstr[0]

        # Instr of the form INST SRC1 SRC2 DST1
        if opcode in [1, 2]:
            assert(len(self._curinstr) == 4)

            self._opcode = opcode
            self._src1 = self._curinstr[1]
            self._src2 = self._curinstr[2]
            self._dst1 = self._curinstr[3]

            assert(len(self._memory) > self._src1)
            assert(len(self._memory) > self._src2)
            assert(len(self._memory) > self._dst1)

            self._src1val = self._memory[self._src1]
            self._src2val = self._memory[self._src2]

        # Instr of the form INST
        elif opcode in [99]:
            assert(len(self._curinstr) == 1)

            self._opcode = opcode

        else:
            self._halted = True
            print("Encountered unknown opcode! {0}".format(self._curinstr))

    def execute_instruction(self):

        # ADD: DST1 = SRC1 + SRC2
        if self._opcode == 1:
            self._res = self._src1val + self._src2val

        # MUL: DST1 = SRC1 * SRC2
        elif self._opcode == 2:
            self._res = self._src1val * self._src2val
          
        # HALT
        elif self._opcode == 99:
            self._halted = True

        else:
            self._halted = True
            print("Encountered unknown opcode! {0}".format(self._curinstr)) 

    def writeback_instruction(self):
        
        if self._opcode in [1,2]:
            self._memory[self._dst1] = self._res

        # Clean up
        self._curinstr = None
        self._opcode = None
        self._src1 = None
        self._src2 = None
        self._src1val = None
        self._src2val = None
        self._dst1 = None
        self._res = None

    def run_program(self):
        while not self._halted and self._pc < len(self._memory):
            self.fetch_instruction()
            self.decode_instruction()
            self.execute_instruction()
            self.writeback_instruction()

    def print_cur_instr(self):
        
        assert(len(self._curinstr) > 0)
        opcode = self._curinstr[0]
        if opcode == 1:
            assert(len(self._curinstr) == 4)
            src1 = self._curinstr[1]
            src2 = self._curinstr[2]
            dst1 = self._curinstr[3]
            assert(src1 < len(self._memory))
            assert(src2 < len(self._memory))
            assert(dst1 < len(self._memory))
            src1val = self._memory[src1]
            src2val = self._memory[src2]
            res = src1val + src2val
            print("ADD\t${0} ({1})\t+ ${2} ({3})\t= {4} -> ${5}".format(src1, src1val, src2, src2val, res, dst1))

        if opcode == 2:
            assert(len(self._curinstr) == 4)
            src1 = self._curinstr[1]
            src2 = self._curinstr[2]
            dst1 = self._curinstr[3]
            assert(src1 < len(self._memory))
            assert(src2 < len(self._memory))
            assert(dst1 < len(self._memory))
            src1val = self._memory[src1]
            src2val = self._memory[src2]
            res = src1val * src2val
            print("MUL\t${0} ({1})\t* ${2} ({3})\t= {4} -> ${5}".format(src1, src1val, src2, src2val, res, dst1))
            
        if opcode == 99:
            print("HALT")

    def print_cur_mem(self):
        
        off = 0
        while off < len(self._memory):
            if self._memory[off] in [1, 2]:
                if off + 3 < len(self._memory):
                    print("{0}\t{1}\t{2}\t{3}".format(self._memory[off],
                                                      self._memory[off+1],
                                                      self._memory[off+2],
                                                      self._memory[off+3]))
                    off += 4
                else:
                    # We're at the end of memory anyways
                    [print("{0}\t".format(x), end='') for x in self._memory[off:]]
                    print() 
                    off = len(self._memory)
            elif self._memory[off] in [99]:
                print("{0}".format(self._memory[off]))
                off += 1
            else:
                # Either print 5 elements, or whatever's left
                if off + 4 < len(self._memory):
                    print("{0}\t{1}\t{2}\t{3}\t{4}".format(self._memory[off],
                                                           self._memory[off+1],
                                                           self._memory[off+2],
                                                           self._memory[off+3],
                                                           self._memory[off+4]))
                    off += 5
                else:
                    # We're at the end of memory anyways
                    [print("{0}\t".format(x), end='') for x in self._memory[off:]]
                    print()
                    off = len(self._memory)

def run_program(mem):

    target = 19690720
    noun = 0
    verb = 0

    orig_memory = mem.copy()
    computer = int_code(mem)
    computer._debug = False
    if computer._debug:
        print("===============")
        print("Starting State:")
        computer.print_cur_mem()
        print("===============")
    computer.run_program()
    if computer._debug:
        print("===============")
        print("Ending State:")
        computer.print_cur_mem()
        print("===============")

    inputs = ((noun, verb) for noun in range(100) for verb in range(100))
    for noun, verb in inputs:
        print(noun, verb)

        # Reset to blank state
        new_state = orig_memory.copy()
        computer.reset(new_state)
        computer._debug = False
        
        # Initialize state, and run
        computer._memory[1] = noun
        computer._memory[2] = verb
        computer.run_program()

        # Check against target
        if computer._memory[0] == target:
            print("Found target!")
            print("Noun: {0}\tVerb: {1}".format(noun, verb))
            print("Function: {0}".format(100*noun + verb))
            break

    print("Mem[0]: {0}".format(computer._memory[0]))

if __name__ == "__main__":

    input_filename = "2.input"
    #input_filename = "testcase1.input"
    #input_filename = "testcase2.input"

    with open(input_filename, 'r') as infile:
       lines = infile.readlines()

    mem_input = [int(x) for x in lines[0].rstrip().split(',')]

    run_program(mem_input)

