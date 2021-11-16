<?php

/**
 * Test script for parser and interpret [lang: IPPcode21]
 *
 * PHP version 7.4
 *
 * @file html.php
 * 
 * @author: Martin Zaťovič
 */

class HTMLGenerator
{
	public $html;

	public function __construct()
	{
		$test_count = 0;
		$passed_count = 0;
	}

	public function generate_header()
	{
	
	$this->html = '<!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\">
            <title>Test results for IPPcode21 language</title>
            <meta name=\"Table containing the results of the tests for IPPcode21.\">
            <meta name=\"Martin Zaťovič\">
	</head>';
	}

	public function generate_table_header()
	{
		$this->html = $this->html . '
		<body>
		    <style type="text/css">
			.tg  {border-collapse:collapse;border-spacing:0;width:100%;}
			.tg td{border-color:black;border-style:solid;border-width:3px;font-family:Arial, sans-serif;font-size:14px;
			  overflow:hidden;padding:10px 5px;word-break:normal;}
			.tg th{border-color:black;border-style:solid;border-width:3px;font-family:Arial, sans-serif;font-size:14px;
			  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
			.tg .tg-0lax{text-align:center;font-size:25px;vertical-align:top;}
			.tg .tg-fail{background-color:#fd6864;border-color:black;color:#000000;text-align:center;font-size:25px;vertical-align:top}
			.tg .tg-pass{background-color:#009901;border-color:black;text-align:center;font-size:25px;vertical-align:top}
			</style>
			<table class="tg">
			<thead>
			  <tr>
			    <th class="tg-0lax"><b>test name</b></th>
			    <th class="tg-0lax"><b>parse.php</b></th>
			    <th class="tg-0lax"><b>interpret.py</b></th>
			    <th class="tg-0lax"><b>test result</b></th>
			  </tr>
			</thead>
			';
	}

	public function generate_parse_only_table_header()
	{
		$this->html = $this->html . '
		<body>
		<style type="text/css">
			.tg  {border-collapse:collapse;font-size:25px;border-spacing:0;width:100%;}
			.tg td{border-color:black;border-style:solid;border-width:3px;font-family:Arial, sans-serif;font-size:14px;
			  overflow:hidden;padding:10px 5px;word-break:normal;}
			.tg th{border-color:black;border-style:solid;border-width:3px;font-family:Arial, sans-serif;font-size:14px;
			  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
			.tg .tg-0lax{text-align:center;vertical-align:top}
			.tg .tg-fail{background-color:#fd6864;border-color:black;color:#000000;text-align:center;vertical-align:top}
			.tg .tg-pass{background-color:#009901;border-color:black;text-align:center;vertical-align:top}
			</style>
			<table class="tg">
			<thead>
			  <tr>
			    <th class="tg-0lax">test name</th>
			    <th class="tg-0lax">parse.php</th>
			    <th class="tg-0lax">test result</th>
			  </tr>
			</thead>';
	}

	public function generate_int_only_table_header()
	{
		$this->html = $this->html . '
		<body>
		<style type="text/css">
			.tg  {border-collapse:collapse;font-size:25px;border-spacing:0;width:100%;}
			.tg td{border-color:black;border-style:solid;border-width:3px;font-family:Arial, sans-serif;font-size:14px;
			  overflow:hidden;padding:10px 5px;word-break:normal;}
			.tg th{border-color:black;border-style:solid;border-width:3px;font-family:Arial, sans-serif;font-size:14px;
			  font-weight:normal;overflow:hidden;padding:10px 5px;word-break:normal;}
			.tg .tg-0lax{text-align:center;vertical-align:top;}
			.tg .tg-fail{background-color:#fd6864;border-color:black;color:#000000;text-align:center;vertical-align:top}
			.tg .tg-pass{background-color:#009901;border-color:black;text-align:center;vertical-align:top}
			</style>
			<table class="tg">
			<thead>
			  <tr>
			    <th class="tg-0lax">test name</th>
			    <th class="tg-0lax">interpret.py</th>
			    <th class="tg-0lax">test result</th>
			  </tr>
			</thead>';
	}

	public function add_test($test_name, $exp_parse_res, $parse_res, $exp_int_res, $int_res, $test_result)
	{
		$this->html = $this->html . '
			<tbody>
			  <tr>
			    <td class="tg-0lax">' . $test_name . ' </td>
			    <td class="tg-0lax">' . 'Expected result : <b>' . $exp_parse_res . '</b> Real result : <b>' . $parse_res . '</b></td>
			    <td class="tg-0lax">' . 'Expected result : <b>' . $exp_int_res .   '</b> Real result : <b>' . $int_res . '</b></td>';
		if($test_result == "OK") {
			$this->html = $this->html . '
			    <td class="tg-pass">' . $test_result . ' </td>';
		}
		else
		{
			$this->html = $this->html . '
			    <td class="tg-fail">' . $test_result . ' </td>';
		}

		$this->html = $this->html . '
			  </tr>
			</tbody>';
	}

	public function add_test_parse_only($test_name, $exp_parse_res, $parse_res, $test_result)
	{
		$this->html = $this->html . '
			<tbody>
			  <tr>
			    <td class="tg-0lax">' . $test_name . ' </td>
			    <td class="tg-0lax">' . 'Expected result : <b>' . $exp_parse_res . '</b> Real result : <b>' . $parse_res . '</b></td>';
		if($test_result == "OK") {
			$this->html = $this->html . '
			    <td class="tg-pass">' . $test_result . ' </td>';
		}
		else
		{
			$this->html = $this->html . '
			    <td class="tg-fail">' . $test_result . ' </td>';
		}

		$this->html = $this->html . '
			  </tr>
			</tbody>';
	}

	public function add_test_int_only($test_name, $exp_int_res, $int_res, $test_result)
	{
		$this->html = $this->html . '
			<tbody>
			  <tr>
			    <td class="tg-0lax">' . $test_name . ' </td>
			    <td class="tg-0lax">' . 'Expected result : <b>' . $exp_int_res . '</b> Real result : <b>' . $int_res . '</b></td>';

		if($test_result == "OK") {
			$this->html = $this->html . '
			    <td class="tg-pass">' . $test_result . ' </td>';
		}
		else
		{
			$this->html = $this->html . '
			    <td class="tg-fail">' . $test_result . ' </td>';
		}

		$this->html = $this->html . '
			  </tr>
			</tbody>';
	}
	
	public function succeeded($pass_count, $fail_count, $all_passed)
	{
		$ippcode = '
		<p style="font-size:45px;text-align:center;">IPPcode21 Test Files Summary</p>';
		$all_count = $pass_count + $fail_count;
		if($all_passed)
		{
			$str = '
			<p style="font-size:25px;text-align:center;">ALL ' . $pass_count . ' TESTS HAVE PASSED<br>All tests: ' . $all_count . '<br>Passed tests: ' . $pass_count . '<br>Failed tests: ' . $fail_count . '</p>';
			$this->html = str_replace("<body>", "<body>" . $ippcode . $str , $this->html);
		}
		else
		{
			$str = '
			<p style="font-size:25px;text-align:center;">' . 'All tests: ' . $all_count . '<br>Passed tests: ' . $pass_count . '<br>Failed tests: ' . $fail_count . '</p>';
                        $this->html = str_replace("<body>", "<body>" . $ippcode . $str , $this->html);
		}
		
	}

	public function end_html()
	{
		$this->html = $this->html . '   
			</body>
		       </table>
		      </html>';
	}

	public function print_html()
	{
		fwrite(STDOUT, $this->html);
	}
}
