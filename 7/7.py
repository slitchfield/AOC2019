import itertools

class int_code:

    def __init__(self, mem, label="Computer"):

        self._debug = True
        self._label = label

        # State
        self._orig_mem = mem.copy()
        self._memory = self._orig_mem.copy()
        self._pc = 0
        self._halted = False
        self._blocking = False

        # Fetch
        self._curinstr = None
        self._newpc = None

        # Decode
        self._opcode = None
        self._src1 = None
        self._src1imm = False
        self._src1val = None
        self._src2 = None
        self._src2imm = False
        self._src2val = None
        self._dst1 = None

        # Execute
        self._res = None
        self._pcmod = False

        # Writeback

        # Communication
        self._input_from_q = False
        self._input_q = []
        self._output_to_q  = False
        self._output_q = []

    def reset(self):

        self._memory = self._orig_mem.copy()
        self._pc = 0
        self._halted = False
        self._blocking = False

        self._curinstr = None
        self._opcode = None
        self._src1 = None
        self._src1imm = False
        self._src1val = None
        self._src2 = None
        self._src2imm = False
        self._src2val = None
        self._dst1 = None
        self._res = None
        self._newpc = None
        self._pcmod = False

        self._input_q.clear()
        self._output_q.clear()

    def fetch_instruction(self):
        assert (self._pc < len(self._memory))

        opcode = self._memory[self._pc] % 100

        # Instr of the form INST SRC1 SRC2 DST1
        if opcode in [1, 2, 7, 8]:
            assert (self._pc + 3 < len(self._memory))
            self._curinstr = self._memory[self._pc:self._pc + 4]
            self._newpc = self._pc + 4  # Consume 4B

        # Instr of the form INST PARM1
        elif opcode in [3, 4]:
            assert (self._pc + 1 < len(self._memory))
            self._curinstr = self._memory[self._pc:self._pc + 2]
            self._newpc = self._pc + 2  # Consume 2B

        # Instr of the form INST PARM1 PARM2
        elif opcode in [5, 6]:
            assert (self._pc + 2 < len(self._memory))
            self._curinstr = self._memory[self._pc:self._pc + 3]
            self._newpc = self._pc + 3  # Consume 3B

        # Instr of the form INST
        elif opcode in [99]:
            self._curinstr = [self._memory[self._pc]]
            self._newpc = self._pc + 1  # Consume 1B
        else:
            self._halted = True
            print("Encountered unknown opcode! {0}".format(opcode))

    def decode_instruction(self):

        if self._debug:
            self.print_cur_instr()

        assert (len(self._curinstr) > 0)

        opcode = self._curinstr[0] % 100
        imm1 = bool(int(self._curinstr[0] / 100) % 2)
        imm2 = bool(int(self._curinstr[0] / 1000) % 2)
        imm3 = bool(int(self._curinstr[0] / 10000) % 2)

        # ==========
        # Instr of the form INST SRC1 SRC2 DST1
        if opcode in [1, 2, 7, 8]:
            assert (len(self._curinstr) == 4)

            self._opcode = opcode
            self._src1 = self._curinstr[1]
            self._src1imm = imm1
            self._src2 = self._curinstr[2]
            self._src2imm = imm2
            self._dst1 = self._curinstr[3]

            if not imm1:
                assert (len(self._memory) > self._src1)
            if not imm2:
                assert (len(self._memory) > self._src2)
            assert (len(self._memory) > self._dst1)

            if self._src1imm:
                self._src1val = self._src1
            else:
                self._src1val = self._memory[self._src1]

            if self._src2imm:
                self._src2val = self._src2
            else:
                self._src2val = self._memory[self._src2]

        # ==========
        # Instr of the form INST PARM1

        # Input, only parameter is where input is written to
        elif opcode in [3]:
            assert (len(self._curinstr) == 2)

            self._opcode = opcode
            self._dst1 = self._curinstr[1]

        # Output, only parameter is where the output is written from
        elif opcode in [4]:
            assert (len(self._curinstr) == 2)

            self._opcode = opcode
            self._src1 = self._curinstr[1]
            self._src1imm = imm1
            if self._src1imm:
                self._src1val = self._src1
            else:
                self._src1val = self._memory[self._src1]

        # ==========
        # Instr of the form INST PARM1 PARM2
        elif opcode in [5, 6]:
            assert (len(self._curinstr) == 3)

            # Currently both have 2 sources, check for imm
            self._opcode = opcode
            self._src1 = self._curinstr[1]
            self._src1imm = imm1
            if self._src1imm:
                self._src1val = self._src1
            else:
                assert (len(self._memory) > self._src1)
                self._src1val = self._memory[self._src1]
            self._src2 = self._curinstr[2]
            self._src2imm = imm2
            if self._src2imm:
                self._src2val = self._src2
            else:
                assert (len(self._memory) > self._src2)
                self._src2val = self._memory[self._src2]

        # ==========
        # Instr of the form INST
        elif opcode in [99]:
            assert (len(self._curinstr) == 1)

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

        # IN: DST1 = INPUT
        elif self._opcode == 3:
            if self._input_from_q:
                if len(self._input_q) > 0:
                    self._res = self._input_q.pop(0)  # Grab the first element of the queue
                else:
                    # Point back to this instruction and block
                    print(f"({self._label}: Blocking on input")
                    self._newpc = self._pc
                    self._blocking = True
            else:
                self._res = int(input(f"Write input to {self._dst1}:"))

        # OUT: OUTPUT = SRC1
        elif self._opcode == 4:
            if self._output_to_q:
                # Don't need to do check, since we'll just append to output q
                self._output_q.append(self._src1val)
                print(f"OUTQ: {self._src1val}")
            else:
                print(f"OUT: {self._src1val}")

        # JIT: IF SRC1, PC = SRC2
        elif self._opcode == 5:
            if not (self._src1val == 0):
                self._pc = self._src2val
                self._pcmod = True

        # JIF: IF NOT SRC1, PC = SRC2
        elif self._opcode == 6:
            if self._src1val == 0:
                self._pc = self._src2val
                self._pcmod = True

        # LT: IF SRC1 < SRC2, DST1 = 1 ELSE 0
        elif self._opcode == 7:
            if self._src1val < self._src2val:
                self._res = 1
            else:
                self._res = 0

        # EQ: IF SRC1 == SRC2, DST1 = 1 ELSE 0
        elif self._opcode == 8:
            if self._src1val == self._src2val:
                self._res = 1
            else:
                self._res = 0

        # HALT
        elif self._opcode == 99:
            self._halted = True

            # Make sure we stay halted even if someone tries to start us again
            self._newpc = self._pc

        else:
            self._halted = True
            print("Encountered unknown opcode! {0}".format(self._curinstr))

    def writeback_instruction(self):

        # Opcodes that can actually write to memory
        if not self._blocking and self._opcode in [1, 2, 3, 7, 8]:
            self._memory[self._dst1] = self._res

        # Update pc as necessary
        if not self._pcmod:
            self._pc = self._newpc
        else:
            # We took care of the jump, so go back to
            # incrementing
            self._pcmod = False

        # Clean up
        self._curinstr = None
        self._opcode = None
        self._src1 = None
        self._src2 = None
        self._src1imm = False
        self._src2imm = False
        self._src1val = None
        self._src2val = None
        self._dst1 = None
        self._res = None

    def run_program(self):

        # If we're waiting on input and we have it, wake up
        if self._blocking and len(self._input_q) > 0:
            self._blocking = False

        while (not self._blocking) and (not self._halted) and (self._pc < len(self._memory)):
            self.fetch_instruction()
            self.decode_instruction()
            self.execute_instruction()
            self.writeback_instruction()

    def print_cur_instr(self):

        assert (len(self._curinstr) > 0)
        opcode = self._curinstr[0] % 100
        if opcode == 1:
            assert (len(self._curinstr) == 4)
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            imm2 = bool(int(self._curinstr[0] / 1000) % 2)
            imm3 = bool(int(self._curinstr[0] / 10000) % 2)
            src1 = self._curinstr[1]
            src2 = self._curinstr[2]
            dst1 = self._curinstr[3]

            # Check to make sure we don't fall off memory
            if not imm1:
                assert (src1 < len(self._memory))
            if not imm2:
                assert (src2 < len(self._memory))
            assert (dst1 < len(self._memory))

            if imm1:
                src1val = self._curinstr[1]
            else:
                src1val = self._memory[src1]
            if imm2:
                src2val = self._curinstr[2]
            else:
                src2val = self._memory[src2]
            res = src1val + src2val

            print(f"ADD ({self._curinstr[0]})\t", end='')
            if imm1:
                print(f"imm: {src1val}\t", end='')
            else:
                print(f"${src1} ({src1val})\t", end='')
            if imm2:
                print(f"+ imm: {src2val}\t", end='')
            else:
                print(f"${src2} ({src2val})\t", end='')

            print(f"= {res} -> {dst1}")

        if opcode == 2:
            assert (len(self._curinstr) == 4)
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            imm2 = bool(int(self._curinstr[0] / 1000) % 2)
            imm3 = bool(int(self._curinstr[0] / 10000) % 2)
            src1 = self._curinstr[1]
            src2 = self._curinstr[2]
            dst1 = self._curinstr[3]

            if not imm1:
                assert (src1 < len(self._memory))
            if not imm2:
                assert (src2 < len(self._memory))
            assert (dst1 < len(self._memory))

            if imm1:
                src1val = self._curinstr[1]
            else:
                src1val = self._memory[src1]
            if imm2:
                src2val = self._curinstr[2]
            else:
                src2val = self._memory[src2]
            res = src1val * src2val

            print(f"MUL ({self._curinstr[0]})\t", end='')
            if imm1:
                print(f"imm: {src1val}\t", end='')
            else:
                print(f"${src1} ({src1val})\t", end='')
            if imm2:
                print(f"+ imm: {src2val}\t", end='')
            else:
                print(f"${src2} ({src2val})\t", end='')

            print(f"= {res} -> {dst1}")

        if opcode == 3:
            assert (len(self._curinstr) == 2)

            dst1 = self._curinstr[1]
            assert (dst1 < len(self._memory))
            print(f"IN\t", end='')
            print(f"->{dst1}")

        if opcode == 4:
            assert (len(self._curinstr) == 2)

            src1 = self._curinstr[1]
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            if imm1:
                src1val = self._curinstr[1]
            else:
                assert (src1 < len(self._memory))
                src1val = self._memory[src1]

            print(f"OUT\t", end='')
            print(f"<-{src1val}")

        if opcode == 5:
            assert (len(self._curinstr) == 3)

            src1 = self._curinstr[1]
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            if imm1:
                src1val = self._curinstr[1]
            else:
                assert (src1 < len(self._memory))
                src1val = self._memory[src1]
            src2 = self._curinstr[2]
            imm2 = bool(int(self._curinstr[0] / 1000) % 2)
            if imm2:
                src2val = self._curinstr[2]
            else:
                assert (src2 < len(self._memory))
                src2val = self._memory[src2]

            print(f"JIT ({self._curinstr[0]})\t", end='')
            if imm1:
                print(f"imm: {src1val}\t", end='')
            else:
                print(f"${src1} ({src1val})\t", end='')
            if imm2:
                print(f"-> imm: {src2val}\t")
            else:
                print(f"${src2} ({src2val})\t")

        if opcode == 6:
            assert (len(self._curinstr) == 3)

            src1 = self._curinstr[1]
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            if imm1:
                src1val = self._curinstr[1]
            else:
                assert (src1 < len(self._memory))
                src1val = self._memory[src1]
            src2 = self._curinstr[2]
            imm2 = bool(int(self._curinstr[0] / 1000) % 2)
            if imm2:
                src2val = self._curinstr[2]
            else:
                assert (src2 < len(self._memory))
                src2val = self._memory[src2]

            print(f"JIF ({self._curinstr[0]})\t", end='')
            if imm1:
                print(f"imm: {src1val}\t", end='')
            else:
                print(f"${src1} ({src1val})\t", end='')
            if imm2:
                print(f"-> imm: {src2val}\t")
            else:
                print(f"${src2} ({src2val})\t")

        if opcode == 7:
            assert (len(self._curinstr) == 4)
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            imm2 = bool(int(self._curinstr[0] / 1000) % 2)
            imm3 = bool(int(self._curinstr[0] / 10000) % 2)
            src1 = self._curinstr[1]
            src2 = self._curinstr[2]
            dst1 = self._curinstr[3]

            if not imm1:
                assert (src1 < len(self._memory))
            if not imm2:
                assert (src2 < len(self._memory))
            assert (dst1 < len(self._memory))

            if imm1:
                src1val = self._curinstr[1]
            else:
                src1val = self._memory[src1]
            if imm2:
                src2val = self._curinstr[2]
            else:
                src2val = self._memory[src2]
            res = int(src1val < src2val)

            print(f"LT ({self._curinstr[0]})\t", end='')
            if imm1:
                print(f"imm: {src1val}\t", end='')
            else:
                print(f"${src1} ({src1val})\t", end='')
            if imm2:
                print(f"< imm: {src2val}\t", end='')
            else:
                print(f"${src2} ({src2val})\t", end='')

            print(f"= {res} -> {dst1}")

        if opcode == 8:
            assert (len(self._curinstr) == 4)
            imm1 = bool(int(self._curinstr[0] / 100) % 2)
            imm2 = bool(int(self._curinstr[0] / 1000) % 2)
            imm3 = bool(int(self._curinstr[0] / 10000) % 2)
            src1 = self._curinstr[1]
            src2 = self._curinstr[2]
            dst1 = self._curinstr[3]

            if not imm1:
                assert (src1 < len(self._memory))
            if not imm2:
                assert (src2 < len(self._memory))
            assert (dst1 < len(self._memory))

            if imm1:
                src1val = self._curinstr[1]
            else:
                src1val = self._memory[src1]
            if imm2:
                src2val = self._curinstr[2]
            else:
                src2val = self._memory[src2]
            res = int(src1val == src2val)

            print(f"EQ ({self._curinstr[0]})\t", end='')
            if imm1:
                print(f"imm: {src1val}\t", end='')
            else:
                print(f"${src1} ({src1val})\t", end='')
            if imm2:
                print(f"== imm: {src2val}\t", end='')
            else:
                print(f"${src2} ({src2val})\t", end='')

            print(f"= {res} -> {dst1}")

        if opcode == 99:
            print("HALT")

    def print_cur_mem(self):

        off = 0
        while off < len(self._memory):
            if self._memory[off] in [1, 2]:
                if off + 3 < len(self._memory):
                    print("{0}\t{1}\t{2}\t{3}".format(self._memory[off],
                                                      self._memory[off + 1],
                                                      self._memory[off + 2],
                                                      self._memory[off + 3]))
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
                                                           self._memory[off + 1],
                                                           self._memory[off + 2],
                                                           self._memory[off + 3],
                                                           self._memory[off + 4]))
                    off += 5
                else:
                    # We're at the end of memory anyways
                    [print("{0}\t".format(x), end='') for x in self._memory[off:]]
                    print()
                    off = len(self._memory)

def gen_perms(seed, size, n):

    my_list = []

    if size == 1:
        my_list.append(seed)
        return my_list

    for i in range(size):

        my_list.append(gen_perms(seed, size-1, n))

        if size % 2 == 1: # If size odd, swap first and last
            seed[0], seed[size - 1] = seed[size - 1], seed[0]
        else:             # If size even, swap ith and last element
            seed[i], seed[size - 1] = seed[size - 1], seed[i]

    return my_list

def run_program(mem):

    phase_settings = [5, 6, 7, 8, 9]
    perms = itertools.permutations(phase_settings)

    max_settings = None
    max_output = -1

    a_computer = int_code(mem, 'A')
    a_computer._input_from_q = True
    a_computer._output_to_q  = True
    a_computer._debug        = True

    b_computer = int_code(mem, 'B')
    b_computer._input_from_q = True
    b_computer._output_to_q = True
    b_computer._debug = True

    c_computer = int_code(mem, 'C')
    c_computer._input_from_q = True
    c_computer._output_to_q = True
    c_computer._debug = True

    d_computer = int_code(mem, 'D')
    d_computer._input_from_q = True
    d_computer._output_to_q = True
    d_computer._debug = True

    e_computer = int_code(mem, 'E')
    e_computer._input_from_q = True
    e_computer._output_to_q = True
    e_computer._debug = True

    for setting in perms:

        a_first_time = True
        b_first_time = True
        c_first_time = True
        d_first_time = True
        e_first_time = True

        while not (a_computer._halted and b_computer._halted and c_computer._halted and d_computer._halted and e_computer._halted):
            # Run program and get output
            if a_first_time:
                a_computer._input_q.append(setting[0])
                a_computer._input_q.append(0)
                a_first_time = False
            else:
                while len(e_computer._output_q) > 0:
                    a_computer._input_q.append(e_computer._output_q.pop(0))
            a_computer.run_program()

            if b_first_time:
                b_computer._input_q.append(setting[1])
                b_first_time = False

            while len(a_computer._output_q) > 0:
                b_computer._input_q.append(a_computer._output_q.pop(0))
            b_computer.run_program()

            if c_first_time:
                c_computer._input_q.append(setting[2])
                c_first_time = False

            while len(b_computer._output_q) > 0:
                c_computer._input_q.append(b_computer._output_q.pop(0))
            c_computer.run_program()

            if d_first_time:
                d_computer._input_q.append(setting[3])
                d_first_time = False

            while len(c_computer._output_q) > 0:
                d_computer._input_q.append(c_computer._output_q.pop(0))
            d_computer.run_program()

            if e_first_time:
                e_computer._input_q.append(setting[4])
                e_first_time = False

            while len(d_computer._output_q) > 0:
                e_computer._input_q.append(d_computer._output_q.pop(0))
            e_computer.run_program()


        val = e_computer._output_q.pop(0)
        print(f"Final Output: {val}")

        if val > max_output:
            max_output = val
            max_settings = setting

        a_computer.reset()
        b_computer.reset()
        c_computer.reset()
        d_computer.reset()
        e_computer.reset()

    print(f"Found maximum output of {max_output} with settings {max_settings}")

if __name__ == "__main__":
    input_filename = "7.input"
    input_filename = "7_2.input"
    # input_filename = "testcase1.input"
    # input_filename = "testcase2.input"
    # input_filename = "testcase3.input"
    #input_filename = "testcase4.input"
    #input_filename = "testcase5.input"

    with open(input_filename, 'r') as infile:
        lines = infile.readlines()

    mem_input = [int(x) for x in lines[0].rstrip().split(',')]

    run_program(mem_input)

