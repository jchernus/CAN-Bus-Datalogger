<?php

    $file = "/var/tmp/summary/Summary.csv";
	
	exec("python /data/scripts/createSummary.py", $output, $return);
	
	if ($return || !file_exists($file)) {
		die ("Summary file could not be created");
	}

    $type = filetype($file);
    // Get a date and timestamp
    $today = date("F j, Y, g:i a");
    $time = time();
    // Send file headers
    header("Content-type: $type");
    header("Content-Disposition: attachment;filename=Summary.csv");
    header("Content-Transfer-Encoding: binary"); 
    header('Pragma: no-cache'); 
    header('Expires: 0');
    // Send the file contents.
    set_time_limit(0); 
    readfile($file);
?>