<?php

/**
 * Test script for parser and interpret [lang: IPPcode21]
 *
 * PHP version 7.4
 *
 * @file test.php
 * 
 * @author: Martin Zaťovič
 */

include 'modules/html.php';

$recursive;
$directory;
$interpret;
$parser;
$jexamxml;
$jexamcfg;
$parse_only;
$int_only;

class Tester
{
	public $dirs;
	public $testfile_paths;

	public function __construct()
	{
		$this->dirs = [];
		$this->testfile_paths = [];
	}

	public function process_dir()
	{
		global $recursive;
		global $directory;
		global $interpret;
		global $parser;
		global $jexamxml;
		global $jexamcfg;
		global $parse_only;
		global $int_only;

		$passed_tests = 0;
		
		$html = new HTMLGenerator();
		$html->generate_header();

		if($parse_only)
			$html->generate_parse_only_table_header();
		elseif($int_only)
			$html->generate_int_only_table_header();
		else
			$html->generate_table_header();

		if ($recursive)
			exec("find " . $directory . " -regex '.*\.src$'", $testfile_paths);
		else 
			exec("find " . $directory . " -maxdepth 1 -regex '.*\.src$'", $testfile_paths);

		foreach ($testfile_paths as $testfile)
		{
			$test_path_array = explode('/', $testfile);
			$test_name = explode('.', end($test_path_array))[0];
			$test_path = "";

			foreach (array_slice($test_path_array, 0, -1) as $directory)
			{
     				$test_path = $test_path . $directory . '/';
    			}
			
			$in_file_name = $test_path . $test_name . ".in";
			$out_file_name = $test_path . $test_name . ".out";
			$rc_file_name = $test_path . $test_name . ".rc";
			
			if(file_exists($rc_file_name))
			{
				$rc_file = fopen($rc_file_name, "r");
				$ret_code = intval(fread($rc_file, filesize($rc_file_name)));
				fclose($rc_file);
			}
			else
			{
				$ret_code = 0;
				$rc_file = fopen($rc_file_name, "w");
				fwrite($rc_file, "0");
				fclose($rc_file);
			}
			if(!file_exists($in_file_name))
			{
				$in_file = fopen($in_file_name, "w");
				fclose($in_file);
			}
			
			if(!file_exists($out_file_name))
			{
				$out_file = fopen($out_file_name, "w");
				fclose($out_file);
			}

			
			$parser_out = $test_path . $test_name . ".xml";
			$interpret_out = $test_path . $test_name . ".output";

			if($int_only) 
				goto interpret_only_label;

			exec("php7.4 " . $parser . " < " . $testfile, $parser_output_string, $parser_rc);
			$parser_output_string = shell_exec("php7.4 " . $parser . " < " . $testfile);

			$parser_output_file = fopen($parser_out, "w");
			#fprintf(STDOUT, "\n\n" . $parser_output_string . "\n\n");
			fwrite($parser_output_file, $parser_output_string);
			fclose($parser_output_file);

			if($parse_only)
			{
				$jexamxml_output = shell_exec("java -jar " . $jexamxml . " " . $parser_out . " " . $out_file_name . " " . $jexamcfg);
				$jexamxml_output_array = explode("\n", $jexamxml_output);
				
				if($ret_code == 0 and $parser_rc == 0)
				{
					fprintf(STDOUT, $jexamxml_output_array[2]);
					if($jexamxml_output_array[2] != "Two files are identical")
					{
						$html->add_test_parse_only($test_name, $ret_code, $parser_rc, "DIFFERENT OUTPUTS");
						goto unlink_lab;
						continue;
					}
				}

				if($ret_code == $parser_rc)
				{
					$result = "OK";
					$passed_tests += 1;
				}
				else
					$result = "DIFFERENT RETURN CODES";

				#fprintf(STDOUT, $jexamxml_output);
				
				$html->add_test_parse_only($test_name, $ret_code, $parser_rc, $result);
				goto unlink_lab;
				continue;
			}
			
			if($parser_rc == 0)
			{
				interpret_only_label:
				if($int_only)
				{
					fprintf(STDOUT, $testfile);
					exec("python3.8 " . $interpret . " --source=" . $testfile . " --input=" . $in_file_name, $interpret_output_string, $interpret_rc);
			        	$interpret_output_string = shell_exec("python3.8 " . $interpret . " --source=" . $testfile . " --input=" . $in_file_name);
				}
				else
				{
					exec("python3.8 " . $interpret . " --source=" . $parser_out . " --input=" . $in_file_name, $interpret_output_string, $interpret_rc);
			       		$interpret_output_string = shell_exec("python3.8 " . $interpret . " --source=" . $parser_out . " --input=" . $in_file_name);
				}
				
				$interpret_output_file = fopen($interpret_out, "w");
				fwrite($interpret_output_file, $interpret_output_string);
				fclose($interpret_output_file);
				
				$diff = "";

				if (!$interpret_rc)
				{
					$diff = shell_exec("diff " . $out_file_name . " " . $interpret_out);
					if($diff != "")
					{
						fprintf(STDOUT, "Neni su rovnake");
					}
				}

				if($int_only)
				{
					if($ret_code == 0)
					{
						if($diff != "")
						{
							$html->add_test_int_only($test_name, $ret_code, $interpret_rc, "DIFFERENT OUTPUTS");
							goto unlink_lab;
							continue;
						}
					}

					if($ret_code == $interpret_rc)
					{
						$result = "OK";
						$passed_tests += 1;
					}
					else
						$result = "DIFFERENT RETURN CODES";

					$html->add_test_int_only($test_name, $ret_code, $interpret_rc, $result);
					goto unlink_lab;
					continue;
				}
				else
				{							
					if($ret_code == 0 and $interpret_rc == 0 and $parser_rc == 0)
					{
						if($diff != "")
						{
							$html->add_test($test_name, 0, $parser_rc, $ret_code, $interpret_rc, "DIFFERENT OUTPUTS");
							goto unlink_lab;
							continue;
						}
					}
					
					if($parser_rc != 0)
						$result = "DIFFERENT RC PARSER";

					if($ret_code == $interpret_rc and $parser_rc == 0)
					{
						$result = "OK";
						$passed_tests += 1;
					}
					else
						$result = "DIFFERENT RC INTERPRET";

					$html->add_test($test_name, 0, $parser_rc, $ret_code, $interpret_rc, $result);
					goto unlink_lab;
					continue;
				}
			}
			else
			{
				if($parse_only)
				{
					$html->add_test_parse_only($test_name, 0, $parser_rc, "DIFFERENT PARSER RC");
					goto unlink_lab;
					continue;
				}
				else
				{
					$html->add_test_parse_only($test_name, 0, $parser_rc, "X", "X", "DIFFERENT PARSER RC");
				}

			}
			unlink_lab:
			if(file_exists($parser_out))
				unlink($parser_out);
			if(file_exists($interpret_out))
				unlink($interpret_out);
		}
		$html->end_html();
		$html->succeeded($passed_tests, count($testfile_paths) - $passed_tests, $passed_tests == count($testfile_paths));
		$html->print_html();
	}
}


class Arguments {

	public function __construct()
	{
		global $recursive;
		global $directory;
		global $interpret;
		global $parser;
		global $jexamxml;
		global $jexamcfg;
		global $parse_only;
		global $int_only;

		$recursive = false;
		$directory = getcwd().'/';
		$interpret = './interpret.py';
		$parser = './parse.php';
		$jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar';
		$jexamcfg = '/pub/courses/ipp/jexamxml/options';
		$parse_only = false;
		$int_only = false;
	}

	public function parse_arguments()
	{
		global $argc;
		global $argv;
		
		global $recursive;
		global $directory;
		global $interpret;
		global $parser;
		global $jexamxml;
		global $jexamcfg;
		global $parse_only;
		global $int_only;

		$opts = getopt("", ["help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexamxml:", "jexamcfg:"]);
		
		if( $argc == 1 )
		{
	
		}
		
		if(array_key_exists('help', $opts))
		{
			if($argc != 2)
			{
				fprintf(STDERR, "Help parameter has to be passed as the only parameter of the script.");
				exit(10);
			}
			else
			{
				fprintf(STDOUT, "Script for testing IPPcode21 parser and interpret.");
				exit(0);
			}
		}

		if(array_key_exists('directory', $opts))
		{
			$directory = $opts['directory'];
			if($directory[strlen($directory) - 1] != '/')
			{
				$directory.'/';
			}
		}

		if(array_key_exists('recursive', $opts))
		{
			$recursive = true;
		}

		if(array_key_exists('parse-script', $opts))
		{
			$parser = $opts['parse-script'];
		}
		
		if(array_key_exists('int-script', $opts))
		{
			$interpret = $opts['int-script'];
		}
		
		if(array_key_exists('parse-only', $opts))
		{
			if(array_key_exists('int-only', $opts) or array_key_exists('int-script', $opts))
			{
				frpintf(STDERR, "Parameter --parse-only can not be combined with --int-only or --int-script");
				exit(10);
			}
			$parse_only = true;
		}
		
		if(array_key_exists('int-only', $opts))
		{
			if(array_key_exists('parse-only', $opts) or array_key_exists('parse-script', $opts))
			{
				frpintf(STDERR, "Parameter --int-only can not be combined with --parse-only or --parse-script");
				exit(10);
			}
			$int_only = true;
		}
		
		if(array_key_exists('jexamxml', $opts))
		{
			$jexamxml = $opts['jexamxml'];
		}
		
		if(array_key_exists('jexamcfg', $opts))
		{
			$jexamcfg = $opts['jexamcfg'];
		}
	
		if (!file_exists($directory))
		{
			fprintf(STDERR, "The test directory does not exist -  ".$directory."\n");
			exit(10);
		}
		if (!file_exists($parser))
		{
			fprintf(STDERR, "The parser file does not exist -  ".$parseScript."\n");
			exit(10);
		}
		if (!file_exists($interpret))
		{
			fprintf(STDERR, "The interpreter file does not exist -  ".$intScript."\n");
			exit(10);
		}
		if (!file_exists($jexamxml) and $parse_only)
		{
			fprintf(STDERR, "The A7Soft JExamXML JAR file does not exist -  ".$jexamxml."\n");
			exit(10);
		}
		if (!file_exists($jexamcfg) and $parse_only)
		{
			fprintf(STDERR, "The A7Soft JExamXML config file does not exist -  ".$jexamcfg."\n");
			exit(10);
		}
		return;
 	}
}

$args = new Arguments();
$args->parse_arguments();

$processor = new Tester();
$processor->process_dir($directory, $recursive, $parser, $interpret);
