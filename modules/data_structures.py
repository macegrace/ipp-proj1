from modules.error import Error

class Stack(Error):
# defines a stack data structure

    def __init__(self):
    # stack constructer   
        self.stack = []
    
    def stack_get(self):
    # returns the whole stack
        return self.stack

    def stack_push(self, type, value):
    # pushes a value onto the stack   
        self.stack.append((value, type))

    def stack_pop(self):
    # pops a value from
        if len(self.stack) <= 0:
            self.exit_with_code(56, "Tried to pop from an empty stack")
        else:
            return self.stack.pop()

class FrameProcessor(Error):
# takes care of frames and calls
    def __init__(self):
    # initializes variables
        self.frame_stack = []
        self.undef_flag = True
        self.frame_buffer = {}
        self.global_frame = {}

    def fbuffer_init(self):
    # initializes frame buffer   
        self.undef_flag = False
        self.frame_buffer = {}
    
    def push_fbuffer2fstack(self, ):
    # pushes a frame from a frame buffer onto the frame stack
        if self.undef_flag == False:
            self.frame_stack.append(self.frame_buffer)
        else:
            self.exit_with_code(55, 'Tried to push unexisting temporary frame to stack')
        self.undef_flag = True

    def pop_fstack2fbuffer(self):
    # pops a frame from the frame stack to a frame buffer
        if len(self.frame_stack) > 0:
            self.frame_buffer = self.frame_stack.pop()
            self.undef_flag = False
        else:
            self.exit_with_code(55, 'Tried to pop from an empty frame stack')
    
    def fstack_get(self):
        # returns the whole frame stack
        return self.frame_stack

    def frame_get(self, frame):
    # returns the specified frame
        if frame == 'GF':
            return self.global_frame
        elif frame == 'LF':
            if len(self.frame_stack) > 0:
                return self.frame_stack[len(self.frame_stack) - 1]
            else:
                return 'UNDEFINED'
        elif frame == 'TF':
            if self.undef_flag == True:
                return 'UNDEFINED'
            else:
                return self.frame_buffer

    def name_and_frame_variable(self, ins_operand_variable):
    # returns the name of a variable and a name of the frame it is defined within
        return ins_operand_variable['text'].split('@', 1)

    def value_and_type_argument(self, ins_operand):
    # returns the value and type of an operand 
        if ins_operand['type'] in ['int', 'bool', 'string', 'type', 'label', 'nil']:
            return (ins_operand['text'], ins_operand['type'], False)
        else:
            frame, name = self.name_and_frame_variable(ins_operand)
            curr_frame = self.frame_get(frame)
            if curr_frame == 'UNDEFINED':
                self.exit_with_code(55, 'Tried to read a variable from an undefined frame')
            elif name not in curr_frame:
                self.exit_with_code(54, ' Tried to read a non-existant variable')
            else:
                type = curr_frame[name]['type']
                value = curr_frame[name]['value']
                return (value, type, True)

    def variable_set(self, ins_operand_variable, type, value):
    # sets the new value to ins_operand_variable
        frame, name = self.name_and_frame_variable(ins_operand_variable)
        curr_frame = self.frame_get(frame)
        if curr_frame == 'UNDEFINED':
            self.exit_with_code(55, 'Tried to write to a variable within an undefined frame'.format(frame, name))
        elif name not in curr_frame:
            self.exit_with_code(54, 'Tried to write to a non-existant variable'.format(frame, name))
        else:
            #variable exists
            curr_frame[name]['type'] = type
            curr_frame[name]['value'] = value

    def defvar(self, ins_operand):
    # defines a variable
        frame, name = self.name_and_frame_variable(ins_operand)
        frame_to_insert = self.frame_get(frame)
        if frame_to_insert == 'UNDEFINED':
            self.exit_with_code(55, 'Tried to define a variable within an undefined frame')
        else:
            if name not in frame_to_insert:
                frame_to_insert[name] = {'value': None, 'type': None}
            else:
                self.exit_with_code(52, 'Tried to re-define a variable within a frame')

class InstructionHolder(Error):
    def __init__(self):
    # initializes variables
        self.instructions = {}      # instruction dict
        self.labels = {}            # label dict
        self.cstack = []            # stack for calling of functions
    
        self.inst_count_all = 0     # contains count of all the instructions
        self.inst_counter = 1       # tmp counter
        self.inst_exec_counter = 0  # counter of executed instructions
    
    def ilist_add(self, instruction):
    # adds an instruction to the list of instructions
        self.inst_count_all += 1
        self.instructions[self.inst_count_all] = instruction
    
        if instruction.opcode == 'LABEL':
        # if the instruction defines a label, add it to label dict
            label_name = instruction.operand1['text']
            if label_name not in self.labels:
                # save the position in code   
                self.labels[label_name] = self.inst_count_all
            else:
                self.exit_with_code(52, 'A label with this name already exists')

    def ilist_get(self, parser_xml):
    # returns the next instruction from the list of instructions
        if self.inst_counter <= self.inst_count_all:
            self.inst_counter += 1
            self.inst_exec_counter += 1
            self.inst_pos = parser_xml.get_min_order_index()
            if self.inst_pos == -1:
                return None
            else:
                return self.instructions[self.inst_pos + 1]
        else:
            return None
    
    def cstack_push_next(self):
    # pushes the number of the next instruction onto the call stack
        self.cstack.append(self.position_in_code()+1)

    def cstack_pop(self):
    # pops a value from a call stack and sets it for reading
        if len(self.cstack) <= 0:
            self.exit_with_code(56, 'Tried to pop a non-existant value from the call stack')
        else:
            self.inst_counter = self.cstack.pop()

    def label_jump(self, ins_operand_label):
    # sets the currently read instruction to a value of a given label
        label = ins_operand_label['text']
        if label not in self.labels:
            self.exit_with_code(52, 'Tried to jump to a non-existant label')
        else:
            self.inst_counter = self.labels[label]
    
    def position_in_code(self):
    # returns current position in code
        return self.inst_counter -1

    def executed_count(self):
    # returns the count of executed instructions
        return self.inst_exec_counter - 1 
