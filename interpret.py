import sys
import fileinput

from modules.error import Error
from modules.data_structures import FrameProcessor, Stack, InstructionHolder
from modules.parse_inputs import ParserXML, Arguments
from modules.instruction import Instruction

def print_stats(inst_holder, stack, frame_processor):
    print('\nPosition in the code:' , inst_holder.position_in_code() , file=sys.stderr)
    print('Instructions executed:', inst_holder.executed_count(), file=sys.stderr)
    print('Data Stack : ', stack.stack_get(), ' Totally: ', len(stack.stack_get()), file=sys.stderr)
    print('Frame Stack: ', frame_processor.fstack_get(), ' Totally: ', len(frame_processor.fstack_get()), '\n', file=sys.stderr) 

def Main(): 
    error = Error()
    stack = Stack()
    frame_processor = FrameProcessor()
    
    arguments = Arguments()
    arguments.process()

    inst_holder = InstructionHolder()
    
    parser_xml = ParserXML(arguments.get_source_path(), inst_holder)
    parser_xml.process()

    while 1:
        curr_inst = inst_holder.ilist_get(parser_xml) # load next instruction
        
        if curr_inst is not None:
            op = curr_inst.opcode
        else: 
            # if no more instructions are loaded, the cycle breaks
            break
        
        # Process FRAME instructions
        if op == 'MOVE':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand2)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            frame_processor.variable_set(curr_inst.operand1, type, value)
        
        elif op == 'CREATEFRAME':
            frame_processor.fbuffer_init()
        
        elif op == 'PUSHFRAME':
            frame_processor.push_fbuffer2fstack()
        
        elif op == 'POPFRAME':
            frame_processor.pop_fstack2fbuffer()
        
        elif op == 'DEFVAR':
            frame_processor.defvar(curr_inst.operand1)
        
        elif op == 'CALL':
            inst_holder.cstack_push_next() # pushes the position of the next instruction to the call stack
            inst_holder.label_jump(curr_inst.operand1)
        
        elif op == 'RETURN':
            inst_holder.cstack_pop()
        
        # Process STACK instructions
        elif op == 'PUSHS':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand1)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            stack.stack_push(value, type)
        
        elif op == 'POPS':
            value, type = stack.stack_pop()
            if type != None:
                frame_processor.variable_set(curr_inst.operand1, value, type)
            else:
                error.exit_with_code(56, "Missing value, or type")

        # Process ARITHMETIC, RELATIONAL, BOOLEAN and CONVERSION instructions
        elif op in ['ADD', 'SUB', 'MUL', 'IDIV']:
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type1 == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == type2 == 'int':
                if op == 'ADD':
                    frame_processor.variable_set(curr_inst.operand1, 'int', str(int(value1)+int(value2)))
                elif op == 'SUB':
                    frame_processor.variable_set(curr_inst.operand1, 'int', str(int(value1) - int(value2)))
                elif op == 'MUL':
                    frame_processor.variable_set(curr_inst.operand1, 'int', str(int(value1) * int(value2)))
                elif op == 'IDIV':
                    if int(value2) != 0:
                        frame_processor.variable_set(curr_inst.operand1, 'int', str(int(value1) // int(value2)))
                    else:
                        error.exit_with_code(57, 'Division by zero.')
            else:
                error.exit_with_code(53, 'Invalid operand types of the instruction' )
        
        elif op in ['LT', 'GT', 'EQ']:
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type1 == 'nil' and type2 != 'nil' and op != 'EQ':
                error.exit_with_code(53, 'Invalid operand types of the instruction');
            if type2 == 'nil' and type1 != 'nil' and op != 'EQ':
                error.exit_with_code(53, 'Invalid operand types of the instruction');
            if type1 == 'nil' and type2 == 'nil':
                error.exit_with_code(53, 'Invalid operand types of the instruction');

            if type1 == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == type2:
                if op == 'EQ':
                    if value1 == value2:
                        result = 'true'
                    else:
                        result = 'false'
                    frame_processor.variable_set(curr_inst.operand1, 'bool', result)
                elif op == 'LT':
                    if type1 == 'int':
                        if int(value1) < int(value2):
                            less_than = 'true'
                        else:
                            less_than = 'false'
                        frame_processor.variable_set(curr_inst.operand1, 'bool', less_than)
                    elif type1 == 'bool':
                        less_than = 'true' 
                        if value1 == 'false' and value2 == 'true':
                            less_than = 'true'
                        else:
                            less_than = 'false'
                        frame_processor.variable_set(curr_inst.operand1, 'bool', less_than)
                    else:
                        if value1 < value2:
                            less_than = 'true' 
                        else:
                            less_than = 'false' 
                        frame_processor.variable_set(curr_inst.operand1, 'bool', less_than)
                else:
                    if type1 == 'int':
                        if int(value1) > int(value2):
                            greater_than = 'true'
                        else:
                            greater_than = 'false'
                        frame_processor.variable_set(curr_inst.operand1, 'bool', greater_than)
                    elif type1 == 'bool':
                        if value1 == 'true' and value2 == 'false':
                            greater_than = 'true' 
                        else:
                            greater_than = 'false'
                        frame_processor.variable_set(curr_inst.operand1, 'bool', greater_than)
                    else:
                        if value1 > value2:
                            greater_than = 'true' 
                        else:
                            greater_than = 'false'
                        frame_processor.variable_set(curr_inst.operand1, 'bool', greater_than)
            else:
                error.exit_with_code(53, 'Operands of the instruction are of different types')
        
        elif op in ['AND', 'OR']:
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type1 == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == type2 == 'bool':
                if op == 'AND':
                    if value1 == value2 == 'true':
                        and_result = 'true'
                    else:
                        and_result = 'false'
                    frame_processor.variable_set(curr_inst.operand1, 'bool', and_result)
                else:
                    if 'true' in [value1, value2]:
                        and_result = 'true'
                    else:
                        and_result = 'false'
                    frame_processor.variable_set(curr_inst.operand1, 'bool', and_result)
            else:
                error.exit_with_code(53, 'Invalid operand types of the instruction')
        
        elif op == 'NOT':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand2)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            if type == 'bool':
                if value == 'false':
                    not_result = 'true'
                else:
                    not_result = 'false'
                frame_processor.variable_set(curr_inst.operand1, 'bool', not_result)
            else:
                error.exit_with_code(53, 'Invalid type of the operand of NOT instruction')
        
        elif op == 'INT2CHAR':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand2)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            if type == 'int':
                try:
                    char = chr(int(value))
                except ValueError:
                    error.exit_with_code(58, 'Invalid integer operand value of the SETCHAR value (can not be re-typed to char)')
                frame_processor.variable_set(curr_inst.operand1, 'string', char)
            else:
                error.exit_with_code(53, 'Invalid operand types of the instruction INT2CHAR')
        
        elif op == 'STRI2INT':
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == 'string' and type2 == 'int':
                index = int(value2)
                if index >= 0 and index <= len(value1)-1:
                    ordinal = ord(value1[index])
                    frame_processor.variable_set(curr_inst.operand1, 'int', ordinal)
                else:
                    error.exit_with_code(58, 'STR2INT tried to read from an index of a string that is not within its boundaries')
            else:
                error.exit_with_code(53, 'Invalid operand types of the instruction STR2INT')

        # Process INPUT, OUTPUT instructions
        elif op in  ['WRITE', 'DPRINT']:
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand1)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            if type == 'nil':
                continue
            if value is None:
                error.exit_with_code(56, 'Tried to read an uninitialized variable')
            if op == 'WRITE':
                print(value, end='')
            else:
                print(value, file=sys.stderr)
        
        elif op == 'READ':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand2)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            
            if arguments.get_input_path() == 'stdin':
                try:
                    input_s = input()
                except Exception:
                    input_s = ''
            else:
                input_s = arguments.get_next_input()

            if input_s == "$$@@NO_INPUT@@$$":
                frame_processor.variable_set(curr_inst.operand1, 'nil', 'nil')
                continue

            if value == 'int':
                try:
                    input_s = int(input_s)
                except Exception:
                    input_s = 0
                finally:
                    frame_processor.variable_set(curr_inst.operand1, 'int', input_s)
            elif value == 'bool':
                if input_s.lower() == 'true':
                    input_s = 'true'
                else:
                    input_s = 'false'
                frame_processor.variable_set(curr_inst.operand1, 'bool', input_s)
            else:
                try:
                    input_s = str(input_s)
                except Exception:
                    input_s = ''
                finally:
                    frame_processor.variable_set(curr_inst.operand1, 'string', input_s)


        # Process STRING instructions
        elif op == 'CONCAT':
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type1 == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == type2 == 'string':
                frame_processor.variable_set(curr_inst.operand1, 'string', value1+value2)
            else:
                    error.exit_with_code(53, 'Invalid operand types of the instruction CONCAT')
        
        elif op == 'STRLEN':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand2)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            if type == 'string':
                frame_processor.variable_set(curr_inst.operand1, 'int', len(value))
            else:
                if inside_var:
                    error.exit_with_code(53, 'An operand of the STRLEN instruction is not of string type')
                else:
                    error.exit_with_code(53, 'An operand of the STRLEN instruction is not of string type')
        
        elif op == 'GETCHAR':
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type1 == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == 'string' and type2 == 'int':
                index = int(value2)
                if index >= 0 and index <= len(value1)-1:
                    frame_processor.variable_set(curr_inst.operand1, 'string', value1[index])
                else:
                    error.exit_with_code(58, 'GETCHAR tried to get an index of a string that is not within its boundaries')
            else:
                error.exit_with_code(53, 'Invalid operand types of the getchar instruction (accepts string and int)')
        
        elif op == 'SETCHAR':
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand1)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value3, type3, inside_var3 = frame_processor.value_and_type_argument(curr_inst.operand3)
            if type1 == None or type2 == None or type3 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == 'string' and type2 == 'int' and type3 == 'string':
                index = int(value2)
                if value3 == '':
                    error.exit_with_code(58, 'Empty replacement symbol of SETCHAR instruction')
                elif not (index >= 0 and index <= len(value1)-1):
                    error.exit_with_code(58, 'SETCHAR tried to write to an index of a string that is not within its boundaries')
                else:
                    value1 = list(value1)
                    value1[index] = value3[0]
                    value1 = ''.join(value1)
                    frame_processor.variable_set(curr_inst.operand1, 'string', value1)
            else:
                error.exit_with_code(53, 'Invalid operand types of the instruction SETCHAR')
        
        # Process TYPE instruction
        elif op == 'TYPE':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand2)
            if type is None:
                type = ''
            frame_processor.variable_set(curr_inst.operand1, 'string', type)

        # Process LABEL instructions
        elif op == 'LABEL':
            continue
        
        elif op == 'JUMP':
            inst_holder.label_jump(curr_inst.operand1)
        
        elif op in ['JUMPIFEQ', 'JUMPIFNEQ']:
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand1)
            value1, type1, inside_var1 = frame_processor.value_and_type_argument(curr_inst.operand2)
            value2, type2, inside_var2 = frame_processor.value_and_type_argument(curr_inst.operand3)
            
            if value not in inst_holder.labels:
                error.exit_with_code(52, 'Tried to jump to a non-existant label')

            if type1 == None or type2 == None:
                error.exit_with_code(56, "Missing value, or type")
            if type1 == type2:
                if op == 'JUMPIFEQ' and value1 == value2:
                    inst_holder.label_jump(curr_inst.operand1)
                elif op == 'JUMPIFNEQ' and value1 != value2:
                    inst_holder.label_jump(curr_inst.operand1)
                else:
                    pass
            else:
                error.exit_with_code(53, 'The operands of the instruction of different types')
        
        elif op == 'EXIT':
            value, type, inside_var = frame_processor.value_and_type_argument(curr_inst.operand1)
            if type == None:
                error.exit_with_code(56, "Missing value, or type")
            if type == 'int':
                if int(value) > 49 or value[0] == '-':
                    error.exit_with_code(57, 'Invalid exit value(accepted range is 0-49')
                else:
                    print_stats(inst_holder, stack, frame_processor)
                    exit(int(value));
            else:
                error.exit_with_code(53, 'Invalid operand types of the instruction SETCHAR')
   
        
        # Process DEBUG instructions
        if op == 'BREAK':
            print_stats(inst_holder, stack, frame_processor)
            if frame_processor.frame_get('LF') == 'UNDEFINED':
                print('Local Frame (LF): ', frame_processor.frame_get('LF'), file=sys.stderr)
            else:
                print('Global Frame (GF): ', frame_processor.frame_get('GF'), ' , Totally: ', len(frame_processor.frame_get('GF')), file=sys.stderr)
                print('Local Frame (LF): ', frame_processor.frame_get('LF'), ' Totally: ', len(frame_processor.frame_get('LF')), file=sys.stderr)
            if frame_processor.frame_get('TF') == 'UNDEFINED':
                print('Temporary Frame (TF): ', frame_processor.frame_get('TF'), file=sys.stderr)
            else:
                print('Temporary Frame (TF): ', frame_processor.frame_get('TF'), ' Totally: ', len(frame_processor.frame_get('TF')), file=sys.stderr)

if __name__ == '__main__':
    Main()
    exit(0)
