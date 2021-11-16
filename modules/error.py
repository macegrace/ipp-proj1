import sys

class Error():
    def __init__(self):
        pass

    err = {
        10: 'The script is missing a parameter, or unallowed combination of parameters was used',
        11: 'Error opening the input file for reading (e.g. permissions)',
        12: 'Error opening output file for writing (e.g. permissions)',
        
        31: 'Wrong XML format of an input file (the file is not well-formed, or it has unexpected structure)',
        32: 'Error of lexical or syntactic analysis of text elements and attributes in the input XML file (e.g. undefined opcode)',
        
        99: 'Internal error (e.g. memmory allocation error)'
    }

    def exit_with_code(self, error_number, msg=None):
    # prints out an error message to stderr and exits with an error code
        if msg:
            print(msg, file=sys.stderr)
        else:
            print(self.err[error_number], file=sys.stderr)
        exit(error_number)
