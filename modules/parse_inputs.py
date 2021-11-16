from modules.instruction import Instruction
from modules.data_structures import InstructionHolder
from modules.error import Error

import re
import getopt
import sys
import subprocess
import string
import xml.etree.ElementTree as ElementTree

types = ['nil', 'int', 'bool', 'string', 'label', 'type', 'var']

opcodedict = {
    "none" : ("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"),
    "symb" : ("WRITE", "DPRINT", "PUSHS", "EXIT"),
    "lab" : ("CALL", "LABEL", "JUMP"),
    "labsymbsymb" : ("JUMPIFEQ", "JUMPIFNEQ"),
    "var" : ("DEFVAR", "POPS"),
    "vartype" : ("READ"),
    "varsymb" : ("MOVE", "INT2CHAR", "STRLEN", "NOT", "TYPE"),
    "varsymbsymb" : ("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR", "STR2INT", "CONCAT", "GETCHAR", "SETCHAR")
    }

class Arguments(Error):
# class for argument processing
    def __init__(self):
    # initializes variables
        self.source = 'stdin'
        self.input = 'stdin'
        self.input_cnt = -1

    def get_source_path(self):
    # returns source path
        return self.source

    def get_input_path(self):
    # returns input path
        return self.input

    def parse_input_file(self, path):
    # parses the input file by whitespaces and returns as arraz
        word = ''
        with open(path) as file:
            while True:
                char = file.read(1)
                if char.isspace():
                    if word:
                        yield word
                        word = ''
                elif char == '':
                    if word:
                        yield word
                    break
                else:
                    word += char

    def get_next_input(self):
    # returns next input from input arraz
        try:
            ret = next(self.input_arr)
            self.input_cnt += 1
            return ret
        except:
            return "$$@@NO_INPUT@@$$"
        return

    def process(self):
        # processes arguments, calls stdin input if --source or --input is missing
        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ['help', 'source=', 'input='])
        except getopt.GetoptError as error:
            self.exit_with_code(10)

        if self.source == '' and len(opts) == 0:
            return

        if len(opts) > 2:
            self.exit_with_code(10)

        try:
            param1 = opts[0]
            opt1, value1 = param1
        except:
            self.exit_with_code(10)

        try:
            param2 = opts[1]
            opt2, value2 = param2
        except:
            pass

        if opt1 == '--help':
            print('''The program loads a code in IPPcode21 language and its XML representation and interprets it.\n
            Parameters of the script:
            \t--help - prints out help
            \t--source= path to a source XML file
            \t--input= path to an input .IPPcode21 file''')
            exit(0);
        elif opt1 == '--source':
            self.source = value1
        elif opt1 == '--input':
            self.input = value1
        else:
            self.exit_with_code(10)

        try:
            if opt2 == '--help':
                exit_with_code(10)
            elif opt2 == '--source':
                self.source = value2
            elif opt2 == '--input':
                self.input = value2
            else:
                self.exit_with_code(10)
        except:
            pass

        if self.source == 'stdin' and self.input == 'stdin':
            self.exit_with_code(10)

        if self.input != 'stdin':
            self.input_arr = self.parse_input_file(self.input)

class ParserXML(Error):
# class for parsing of XML files
    def __init__(self, source_file_path, inst_list):
    # initializes variables
        self.source_file_path = source_file_path
        self.inst_list = inst_list
        self.inst_order_help = 0
        self.inst_order_save = []
    
    def check_nil(self, arg):
    # checks whether a nil is valid
        if arg.attrib['type'] != 'nil':
            self.exit_with_code(52, 'Wrong or missing type of a nil type')
        if arg.text is None or not 'nil':
            self.exit_with_code(32, 'Wrong argument of nil type')
    def check_type(self, arg):
    # checks whether a type is valid
        if arg.attrib['type'] != 'type':
            self.exit_with_code(52, 'Wrong or missing type attribute of a type')
        if arg.text is None or not re.match('^(int|bool|string)$', arg.text):
            self.exit_with_code(32, 'Wrong type')

    def check_label(self, arg):
    # checks whether a label is valid
        if arg.attrib['type'] != 'label':
            self.exit_with_code(52, 'Wrong or missing type attribute of a label')
        if arg.text is None or not re.match('^(_|-|\$|&|%|\*|[a-zA-Z])(_|-|\$|&|%|\*|[a-zA-Z0-9])*$', arg.text):
            self.exit_with_code(32, 'Wrong or missing label')

    def check_variable(self, arg):
    # checks whether a variable is valid
        if arg.attrib['type'] != 'var':
            print(arg.attrib['type'])
            self.exit_with_code(52, 'Wrong or missing type attribute of a variable')
        if arg.text is None or not re.match('^(GF|LF|TF)@(_|-|\$|&|%|\*|[a-zA-Z])(_|-|\$|&|%|\*|[a-zA-Z0-9])*$', arg.text):
            self.exit_with_code(32, 'Wrong or missing name of a variable')

    def check_symbol(self, arg):
    # checks whether a symbol is valid
        if arg.attrib['type'] == 'int':
            if arg.text is None or not re.match('^([+-]?[1-9][0-9]*|[+-]?[0-9])$', arg.text):
                self.exit_with_code(32, 'Wrong or missing value of int variable')
        elif arg.attrib['type'] == 'bool':
            if arg.text is None or not arg.text in ['true', 'false']:
                self.exit_with_code(32, 'Wrong or missing value of bool variable')
        elif arg.attrib['type'] == 'string':
            if arg.text is None:
                # string muze byt prazdny retezec
                arg.text = ''
            elif not re.search('^(\\\\[0-9]{3}|[^\s\\\\#])*$', arg.text):
                self.exit_with_code(32, 'Wrong or missing value of string variable')
            else:
                # processing escape sequences
                arg.text = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x.group(1))), arg.text)
        elif arg.attrib['type'] == 'nil':
            self.check_nil(arg)
        elif arg.attrib['type'] == 'var':
            self.check_variable(arg)
        else:
            # <symb> musi byt int/bool/string/var
            self.exit_with_code(52, 'Wrong or missing type attribute of a symbol')

    def check_xml_file(self):
    # uses ElementTree to parse an input XML file and checks its structure and syntax
        xmlp = ElementTree.XMLParser(encoding="utf-8")
        with open(self.source_file_path, 'r') as file:
            my_string = file.read()
            file.close()
        
        try:
            tree = ElementTree.parse(self.source_file_path, parser=xmlp)
        except ElementTree.ParseError as e:
            formatted_e = str(e)
            line = int(formatted_e[formatted_e.find("line ") + 5: formatted_e.find(",")])
            column = int(formatted_e[formatted_e.find("column ") + 7:])
            split_str = my_string.split("\n")
            print("{}\n{}^".format(split_str[line - 1], len(split_str[line - 1][0:column])*"-"))
            self.exit_with_code(31, 'The XML file is not well-formed or has invalid structure')
        except FileNotFoundError:
            self.err(11)
        
        self.first = tree.getroot()
        
        if self.first.tag != "program":
            self.exit_with_code(32, "The first element of XML file must be \'program\'.")
        
        allowed_attr = ['language', 'description', 'name']
        for attr in self.first.attrib:
            if attr not in allowed_attr:
                self.exit_with_code(31, "Wrong attributes of program element")
        if 'language' not in self.first.attrib:
            exit_with_code(31, "Language attribute is mandatory within the program element")
        
        if self.first.attrib['language'].lower() != 'ippcode21':
            self.exit_with_code(32, "Only supports IPPcode21 language.")
        
        self.instruction_order_numbers = []

        for inst in self.first:
            if inst.tag != 'instruction':
                self.exit_with_code(32, 'Wrong instruction tag')
            if 'opcode' not in inst.attrib:
                self.exit_with_code(32, 'Missing or wrong attribute /opcode/ in instruction')
            if 'order' not in inst.attrib:
                self.exit_with_code(32, 'Missing or wrong attribute /order/ in instruction')
            else:
                order = inst.attrib['order']
                try:
                    int_order = int(order)
                except:
                    self.exit_with_code(32, 'Invalid order value')
                if(int_order not in self.instruction_order_numbers):
                    self.instruction_order_numbers.append(int_order)
                else:
                    self.exit_with_code(32, "Two instructions have the same order number")
            
            arg_count = 0

            for arg in inst:
                arg_count += 1
                if arg.tag[0] != 'a' or arg.tag[1] != 'r' or arg.tag[2] != 'g':
                    self.exit_with_code(32)
                if 'type' not in arg.attrib:
                    self.exit_with_code(31, 'Missing the type attribute in argument of an instruction')

                global types
                if arg.attrib['type'] not in types:
                    self.exit_with_code(32, 'Undefined type of argument value')
                
                for o in self.instruction_order_numbers:
                    if int(o) <= 0:
                        self.exit_with_code(32, 'Wrong order argument of an instruction')
    
    def get_min_order_index(self):
    # returns the index of the instruction with minimal order that hasnt been processed yet
        while self.inst_order_help not in self.instruction_order_numbers or self.inst_order_help in self.inst_order_save:
            if self.inst_order_help > max(self.instruction_order_numbers):
                return -1
            self.inst_order_help += 1
        self.inst_idx = self.instruction_order_numbers.index(self.inst_order_help)
        self.inst_order_save.append(self.inst_order_help)
        return self.inst_idx

    def check_inst_syntax(self):
    # checks the syntax of instructions
        global opcodedict
        
        def count_args(instruction):
        # returns total number of instruction
            return len(list(instruction))
            
        for instruction in self.first:
            opcode = instruction.attrib['opcode'].upper()
            opcode_type = ""
            try:
                opcode_type = [k for k, v in opcodedict.items() if opcode in v][0]
            except:
                self.exit_with_code(32, "Invalid opcode")
            
            if opcode_type == "none":
                if count_args(instruction) != 0:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                i = Instruction(opcode)
                self.inst_list.ilist_add(i)
            
            elif opcode_type == "symb":
                if count_args(instruction) != 1:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_symbol(instruction[0])
                i = Instruction(opcode, operand1=instruction[0])
                self.inst_list.ilist_add(i)
            
            elif opcode_type == "lab":
                if count_args(instruction) != 1:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_label(instruction[0])
                i = Instruction(opcode, operand1=instruction[0])
                self.inst_list.ilist_add(i)
            
            elif opcode_type == "labsymbsymb":
                if count_args(instruction) != 3:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_label(instruction[0])
                self.check_symbol(instruction[1])
                self.check_symbol(instruction[2])
                i = Instruction(opcode, operand1=instruction[0], operand2=instruction[1], operand3=instruction[2])
                self.inst_list.ilist_add(i)
            
            elif opcode_type == "var":
                if count_args(instruction) != 1:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_variable(instruction[0])
                i = Instruction(opcode, operand1=instruction[0])
                self.inst_list.ilist_add(i)              

            elif opcode_type == "vartype":
                if count_args(instruction) != 2:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_variable(instruction[0])
                self.check_type(instruction[1])
                i = Instruction(opcode, operand1=instruction[0], operand2=instruction[1])
                self.inst_list.ilist_add(i)

            elif opcode_type == "varsymb":
                if count_args(instruction) != 2:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_variable(instruction[0])
                self.check_symbol(instruction[1])
                i = Instruction(opcode, operand1=instruction[0], operand2=instruction[1])
                self.inst_list.ilist_add(i)

            elif opcode_type == "varsymbsymb":
                if count_args(instruction) != 3:
                    self.exit_with_code(32, "Wrong amount of arguments of an instruction")
                self.check_variable(instruction[0])
                self.check_symbol(instruction[1])
                self.check_symbol(instruction[2])
                i = Instruction(opcode, operand1=instruction[0], operand2=instruction[1], operand3=instruction[2])
                self.inst_list.ilist_add(i)

    def process(self):
    # processor
        self.check_xml_file()
        self.check_inst_syntax()
