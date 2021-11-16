class Instruction():
    
    def __init__(self, opcode, operand1=None, operand2=None, operand3=None):
    # initializes variables
        self.opcode = opcode
        self.arg_count = 0
        
        # scans the operands and saves their values and types
        if operand1 is not None:
            self.operand1 = {'text': operand1.text, 'type': operand1.attrib['type']}
            self.arg_count += 1

        if operand2 is not None:
            self.operand2 = {'text': operand2.text, 'type': operand2.attrib['type']}
            self.arg_count += 1

        if operand3 is not None:
            self.operand3 = {'text': operand3.text, 'type': operand3.attrib['type']}
            self.arg_count += 1
