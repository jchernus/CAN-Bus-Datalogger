<?php

    $file = "/var/tmp/logs/";
	
	$listFiles = "";
	foreach ($_POST['select_logs'] as $param_name => $param_val) {
		$listFiles = $listFiles . $param_val . " ";
	}
	$listFiles = substr($listFiles, 0, -1);
	
	exec("cd " . $file . "; python /data/scripts/createZipLogs.py " . $listFiles, $output, $return);
		
	if ($output != "" || $output !== null) {
		$file = $file . $output[0];
	}
	
	if ($return || !file_exists($file)) {
		die ("Summary file could not be created");
	}

    $type = filetype($file);
    // Get a date and timestamp
    $today = date("F j, Y, g:i a");
    $time = time();
    // Send file headers
    header("Content-type: $type");
    header("Content-Disposition: attachment;filename=" . $output[0]);
    header("Content-Transfer-Encoding: binary"); 
    header('Pragma: no-cache'); 
    header('Expires: 0');
    // Send the file contents.
    set_time_limit(0); 
    readfile($file);
?>