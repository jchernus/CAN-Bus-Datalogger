<!DOCTYPE html>
<html lang="en">
  <head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <title>Marmot D&D</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="assets\css\bootstrap.css" rel="stylesheet">
    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
    </style>
    <link href="assets\css\bootstrap-responsive.css" rel="stylesheet">

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="../assets/js/html5shiv.js"></script>
    <![endif]-->

    <!-- Fav and touch icons -->
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="assets/ico/apple-touch-icon-144-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="assets/ico/apple-touch-icon-114-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="72x72" href="assets/ico/apple-touch-icon-72-precomposed.png">
    <link rel="apple-touch-icon-precomposed" href="assets/ico/apple-touch-icon-57-precomposed.png">
    <link rel="shortcut icon" href="assets/ico/favicon.png">
	<style type="text/css"></style>
  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <button type="button" class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="brand" href="index.php">Marmot Web Interface</a>
          <div class="nav-collapse collapse">
            <ul class="nav">
              <li><a href="index.php">Overview</a></li>
              <li class="active"><a href="datalogs.php">Logging</a></li>
              <li><a href="diagnostics.php">Diagnostics</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">
      <h1>Data Logs</h1>
      <p>Daily summaries, as well as detailed logs can be found on this page.</p>
	  
    </div class="container"> <!-- /container -->
	
	<div class="container">
		<h4>Summary</h4>
		<table class="table table-striped">
			<thead>
				<tr>
					<td>Date</td>
					<td>Odometer [km]</td>
					<td>Energy Out [kWh]</td>
					<td>Energy In [kWh]</td>
					<td>Hours Charging [h]</td>
					<td>Hours On [h]</td>
					<td>Hours Driving [h]</td>
				</tr>
			</thead>
			<tbody>
			
				<?php
					class MyDB extends SQLite3
					{
						function __construct()
						{
							$this->open('/data/summary/Summary.db');
						}
					}
					$db = new MyDB();
					if(!$db){
						echo $db->lastErrorMsg();
					}
				   
					$sql = "SELECT * FROM log ORDER BY date DESC LIMIT 8;";
					$ret = $db->query($sql);
					while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
						echo "<tr>";
							echo "<td>" . $row['date'] . "</td>";
							echo "<td>" . $row['odometer'] . "</td>";
							echo "<td>" . $row['energy_in'] . "</td>";
							echo "<td>" . $row['energy_out'] . "</td>";
							echo "<td>" . $row['hours_charging'] . "</td>";
							echo "<td>" . $row['hours_operating'] . "</td>";
							echo "<td>" . $row['hours_running'] . "</td>";
						echo "</tr>";
				   }
				   $db->close();
				?>
				</tr>
			</tbody>
		</table>
		
		<div class="col-sm-offset-2 col-sm-10">
			<a href="summary.php">Download Summary Log</a>
		</div>
		
		<br>
	</div class="container"> <!-- /container -->
	
	<div class="container">
		<h4>Detailed Logs</h4>
		<p>Please select the days for which you would like to download logs, then press Download. Logs will be downloaded in a zip folder.</p>
		<select multiple class="form-control" style="height:250px">
			<option>2015-06-02</option>
			<option>2015-06-01</option>
			<option>2015-05-31</option>
			<option>2015-05-30</option>
			<option>2015-05-29</option>
		</select>
		
		<div class="col-sm-offset-2 col-sm-10">
			<button type="submit" class="btn btn-default" name="download_logs">Download</button>
		</div>
    </div class="container"> <!-- /container -->

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="assets/js/jquery.js"></script>
    <script src="assets/js/bootstrap-transition.js"></script>
    <script src="assets/js/bootstrap-alert.js"></script>
    <script src="assets/js/bootstrap-modal.js"></script>
    <script src="assets/js/bootstrap-dropdown.js"></script>
    <script src="assets/js/bootstrap-scrollspy.js"></script>
    <script src="assets/js/bootstrap-tab.js"></script>
    <script src="assets/js/bootstrap-tooltip.js"></script>
    <script src="assets/js/bootstrap-popover.js"></script>
    <script src="assets/js/bootstrap-button.js"></script>
    <script src="assets/js/bootstrap-collapse.js"></script>
    <script src="assets/js/bootstrap-carousel.js"></script>
    <script src="assets/js/bootstrap-typeahead.js"></script>

</body></html>