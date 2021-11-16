#!/usr/bin/env php
<?php

/**
 * Script for lexical and syntactic analysis [lang: IPPcode21]
 * 
 * PHP vsersion 7.4
 * 
 * @file parse.php
 * 
 * @author Martin Zaťovič (xzatov00)
 */

    ini_set('display_errors', 'stderr');

    // argument processing
    $params = array("help");
    $used_params = getopt(null, $params);
    global $argc;

    if(array_key_exists('help', $used_params))
    {
        if($argc != 2) {
        fputs(STDOUT, "Parameter 'help' may only be used as the only paramater.");
        exit(10);
        }

        fputs(STDOUT, "Script of filter type (parse.php in language PHP 7.4)\n");
	fputs(STDOUT, "loads input source code in IPP-code21 from standard\n");
	fputs(STDOUT, "input, checks its lexical and syntactic correctness\n");
	fputs(STDOUT, "and prints out an XML representation of the code into\n");
	fputs(STDOUT, "standard output\n");
        exit(0);
    }
	
    global $line_cnt;
    $line_cnt = 0;

    // get and process header
    $input = "";
    while(strcmp($input, "") == 0)
    {
        if( !($input = fgets(STDIN)) )
        {
        fputs(STDOUT, "Invalid or missing header in input file.\n");
        exit(21);
        }
        $input = preg_replace("/#.*$/", "", $input, -1, $found);
        $input = strtolower($input);
        $input = trim($input);
        $line_cnt++;
    }

    // find and check header /first lines could be comments/
    if(strcmp($input,".ippcode21")  != 0)
    {
        fputs(STDOUT, "Invalid or missing header in input file.\n");
        exit(21);
    }

    // create DomDoc and its header
    $doc = new DomDocument("1.0", "UTF-8");
    $doc->formatOutput = true;

    $prog_ele = $doc->createElement("program");
    $prog_ele = $doc->appendChild($prog_ele);
    $language_A = $doc->createAttribute("language");
    $language_A->value = "IPPcode21";
    $prog_ele->appendChild($language_A);

    global $instruct_order;
    $instruct_order = 1;

    // load and process input
    while($input = fgets(STDIN))
    {
        $instruction = new Instruction($input);
        if($instruction->is_empty())
        continue;

        $instr_ele = $doc->createElement("instruction");
        $prog_ele->appendChild($instr_ele);

        $ord_att = $doc->createAttribute("order");
        $ord_att->value = $instruct_order++;
        $instr_ele->appendChild($ord_att);

        $opcode_att = $doc->createAttribute("opcode");
        $opcode_att->value = $instruction->opcode_get();

        $instr_ele->appendChild($opcode_att);
        
        $arg_cnt = $instruction->arg_cnt_get();

        // process arguments
        for($i = 1; $i <= $arg_cnt; $i++)
        {
        
        $arg_ele = $doc->createElement("arg".$i);
        $instr_ele->appendChild($arg_ele);
        
        // print type of argument (XML)
        $type_A = $doc->createAttribute("type");
        $type_A->value = $instruction->arg_type_get($i);
        $arg_ele->appendChild($type_A);

        // print type of argument (XML)
        $arg_type = $doc->createTextNode($instruction->arg_val_get($i));
        $arg_ele->appendChild($arg_type);
        }
        $line_cnt++;
    }

    $doc->save("php://stdout");
    exit(0);

    // class for processing of opcodes
    class Instruction
    {
        private $opcode;
        private $arg = array();
        private $arg_cnt;

        public function __construct($input)
        {
        // separate by spaces
        $parse = preg_split("/[[:blank:]]+/", trim($input), 5, PREG_SPLIT_NO_EMPTY);

        $cnt = count($parse);
        for($i = 0; $i < $cnt; $i++)
        {
            $found = 0;

            // remove comments
            $parse[$i] = @preg_replace("/#.*/", "", $parse[$i], 1, $found);
            if($found)
            {
            $length = ($parse[$i] == "" ? $i : $i + 1);

            if($length == 0)
                $parse = null;
            else
                $parse = array_slice($parse, 0, $length);
            break;
            }
        }
        
        if($parse == null)
            return;

        // fetch opcode
        $this->opcode_set($parse[0]);
        
        if($this->arg_cnt + 1 != count($parse))
        {
            global $line_cnt;
            fputs(STDOUT, "Too many or too few arguments"); 
	    fputs(STDOUT, "for instruction (line '$line_cnt')\n");
            exit(23);
        }

        // fetch arguments
        for($i = 0; $i < $this->arg_cnt; $i++)
            $this->arg[$i]->set_value($parse[$i+1]);
        }
        
        public function opcode_get()
        {
        return $this->opcode;
        }

        public function arg_val_get($num)
        {
        return $this->arg[$num-1]->get_value();
        }
        
        public function arg_cnt_get()
        {
        return $this->arg_cnt;
        }

        public function arg_type_get($num)
        {
        return $this->arg[$num-1]->get_type();
        }
        
        public function is_empty()
        {
        return $this->opcode == null;
        }
        
        // divides opcodes into groups acc. to their argument
        // types and searches for appropriate group
        private function get_group($opcode)
        {
        $grp_arr = array(    
            array("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN", "BREAK"),    // no arguments
            array("WRITE", "DPRINT", "PUSHS", "EXIT"),                // <symb>
            array("CALL", "LABEL", "JUMP"),                        // <label>
            array("JUMPIFEQ", "JUMPIFNEQ"),                        // <label><symb><symb>
            array("DEFVAR", "POPS"),                        // <var>
            array("READ"),                                // <var><type>
            array("MOVE", "INT2CHAR", "STRLEN", "NOT", "TYPE"),            // <var><symb>
            array("ADD", "SUB", "MUL", "IDIV", "LT", "GT", "EQ", "AND", "OR",
            "STRI2INT", "CONCAT", "GETCHAR", "SETCHAR")        // <var><symb><symb>
        );
        
        $grp = -1;
        for($i = 0; $i < 8; $i++)
        {
            for($j = 0; $j < count($grp_arr[$i]); $j++)
            {
            if(strcmp($grp_arr[$i][$j], $opcode) == 0)
            {
                $grp = $i;
                break;
            }
            }
        }
        return $grp;
        }

        // evaluate opcode and create objects for their arguments
        private function opcode_set($opcode)
        {
        $opcode = strtoupper($opcode);

        // evaluate group number, see get_group function
        $group = $this->get_group($opcode); 

        if($group == -1)
        {
            global $line_cnt;
            fputs(STDOUT, "Invalid or missing instruction (line $line_cnt)\n");
            exit(22);
        }
        
        // create argument objects
        switch($group)
        {
            case 0:     // OPCODE 'no argument' - nothing to do here
            break;
            case 1:        // OPCODE symb
            $this->arg[0] = new Symbol;
            break;
            case 2:        // OPCODE label
            $this->arg[0] = new Label;
            break;
            case 3:        // OPCODE label symb symb
            $this->arg[0] = new Label;
            $this->arg[1] = new Symbol;
	    $this->arg[2] = new Symbol;
            break;
            case 4:        // OPCODE var
            $this->arg[0] = new Variable;
            break;
            case 5:        // OPCODE var type
            $this->arg[0] = new Variable;
            $this->arg[1] = new Type;
            break;
            case 6:        // OPCODE var symb
            $this->arg[0] = new Variable;
            $this->arg[1] = new Symbol;
            break;
            case 7:        // OPCODE var symb symb
            $this->arg[0] = new Symbol;
            $this->arg[1] = new Symbol;
            $this->arg[2] = new Symbol;
            break;
        }
        $this->arg_cnt = count($this->arg);
        $this->opcode = $opcode;
        }
    }

    abstract class Argument
    {
        protected $value;
        protected $type;

        public function set_value($value)
        {
        if(!$this->fetch_value($value))
        {
            global $line_cnt;
            fputs(STDOUT, "Invalid argument(line $line_cnt)\n");
            exit(23);
        }
        $this->value = $value;
        }
        public function get_value()
        {
        return $this->value;
        }
        
        public function get_type()
        {
        return $this->type;
        }
        
        abstract protected function fetch_value($value);
    }

    class Nil extends Argument
    {
        protected function fetch_value($value)
        {
        $this->type = "nil";
        return ($value == "nil");
        }
    }

    class Variable extends Argument
    {
        public function fetch_value($value)
        {
        $this->type = "var";
        return preg_match("/^(LF|TF|GF)@[[:alpha:]_\-$&%?!*][[:alnum:]_\-$&%?!*]*$/", $value);
        }
    }

    class Symbol extends Argument
    {
        public function set_value($value)
        {
        $this->fetch_value($value);
        }

        protected function fetch_value($value)
        {
        global $line_cnt;

        //checks format of the symbol
        $parse = explode("@", $value, 2);
        if(count($parse) < 2)
        {
            fputs(STDOUT, "There must be a '@' in a definition of a constant(line $line_cnt)\n");
            exit(23);
        }

        switch($parse[0])
        {
            case "nil":
            if($parse[1] != "nil")
            {
                fputs(STDOUT, "Invalid characters in nil type (line $line_cnt)");
                exit(23);
            }
            break;
            case "LF":
            case "TF":
            case "GF":
            if(!preg_match("/^[[:alpha:]_\-$&%?!*][[:alnum:]_\-$&%?!*]*$/", $parse[1]))
            {
                fputs(STDOUT, "Invalid characters in a variable (line $line_cnt)\n");
                exit(23);
            }
            else 
            {
                $parse[0] = "var";
                $parse[1] = $value;
            }
            break;

            case "int":
	    if($parse[1] == "")
		    exit(23);
            if(!preg_match("/^[0-9]*/", $parse[1]))
	    {
                fputs(STDOUT, "Invalid characters in an integer constant : '$parse[1]' (line $line_cnt).\n");
                exit(23);
	    }
            break;
            
            case "string":
            if($parse[1] != "")
	    {
                if(preg_match("/(?!\\\\[0-9]{3})[[:blank:]\\\\#]/", $parse[1]))
                {
                fputs(STDOUT, "Invalid characters in string : '$parse[1]' (line $line_cnt)\n");
                exit(23);
                }
	    }
            break;

            case "bool":
            if($parse[1] != "true" && $parse[1] != "false")
            {
                fputs(STDOUT, "Invalid characters in boolean constant : '$parse[1]' (line $line_cnt)\n");
                exit(23);
            }
            break;
            
            default:
            fputs(STDOUT, "Invalid constant type : $parse[0] (line $line_cnt)\n");
            exit(23);
        }
        $this->type = $parse[0];
        $this->value = $parse[1];
        }
    }

    class Label extends Argument
    {
        protected function fetch_value($value)
        {
        $this->type = "label";
        return preg_match("/^[[:alpha:]_\-$&%?!*][[:alpha:]_\-$&%?!*]*$/", $value);
        }
    }

    class Type extends Argument
    {
        protected function fetch_value($value)
        {
        $this->type = "type";
        return (strcmp($value, "int") == 0 || strcmp($value, "bool") == 0 || strcmp($value, "string") == 0);
        }
    }

?>
