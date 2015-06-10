<!DOCTYPE html>
<html lang="en">
  <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta charset="utf-8">
    <title>Marmot D&D</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="assets/css/bootstrap.css" rel="stylesheet">
    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
    </style>
    <link href="assets/css/bootstrap-responsive.css" rel="stylesheet">

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
  <style type="text/css"></style></head>

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
              <li class="active"><a href="index.php">Overview</a></li>
              <li><a href="datalogs.php">Logging</a></li>
              <li><a href="diagnostics.php">Diagnostics</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>

    <div class="container">
      <h1>Overview</h1>
      <p>Words go here.</p>
    </div class="container"> <!-- /container -->
	
	<div class="container">
		<h4>Marmot Overview</h4>
		<table class="table table-striped" style="width:700px">
			<thead>
				<tr>
					<td>Date</td>
					<td>Time</td>
					<td>SOC</td>
					<td>Battery Current</td>
					<td>Battery Voltage</td>
					<td>Vehicle Speed</td>
					<td>Motor RPM</td>
				</tr>
			</thead>
			<tbody>
				<?php
					class MyDailyLogDB extends SQLite3
					{
						function __construct()
						{
							$this->open('/data/databases/DailyLogs.db');
						}
					}
					$db = new MyDailyLogDB();
					if(!$db){
						echo $db->lastErrorMsg();
					}
					
					$sql = "SELECT * FROM log ORDER BY date DESC, time DESC LIMIT 1;";
					$ret = $db->query($sql);
					while($row = $ret->fetchArray(SQLITE3_ASSOC) ){
						echo "<tr>";
							echo "<td>" . $row['date'] . "</td>";
							echo "<td>" . $row['time'] . "</td>";
							echo "<td>" . $row['soc'] . "</td>";
							echo "<td>" . $row['battery_current'] . "</td>";
							echo "<td>" . $row['battery_voltage'] . "</td>";
							echo "<td>" . $row['vehicle_speed'] . "</td>";
							echo "<td>" . $row['motor_velocity'] . "</td>";
						echo "</tr>";
				   }
				   $db->close();
				?>
			</tbody>
		</table>
		
		<div class="col-sm-offset-2 col-sm-10">
			<button type="submit" class="btn btn-default">Update</button>
		</div>
		
		<br>
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