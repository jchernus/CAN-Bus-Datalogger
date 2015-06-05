<!DOCTYPE html>
<html lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
		<meta charset="utf-8">
		<title>Marmot D&D </title>
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
						<li><a href="datalogs.php">Logging</a></li>
						<li class="active"><a href="diagnostics.php">Diagnostics</a></li>
					</ul>
				</div><!--/.nav-collapse -->
				</div>
			</div>
		</div>

		<div class="container">
			<h1>Battery Pack 1</h1>
			<p></p>
			<br><br>
		</div class="container"> <!-- /container -->
		
		<div class="container">
			<div id="batterychart"></div>
		</div class="container"> <!-- /container -->
	
		
		<script src="http://d3js.org/d3.v2.js"></script>
		<script>
			//Width and height
			var w = 700;
			var h = 200;
			var barPadding = 1;
			
			var dataset = [4.00, 0.1, 3.20, 3.27, 2.8, 2.98, 3.12, 3.05, 3.65, 3.12, 3.05, 3.55, 3.20, 3.27, 2.8, 2.98, 3.12, 3.05, 3.65, 3.27, 2.78, 3.12, 3.05, 3.55];
			
			//Create SVG element
			var svg = d3.select("#batterychart")
						.append("svg")
						.attr("width", w)
						.attr("height", h);

			svg.selectAll("rect")
			   .data(dataset)
			   .enter()
			   .append("rect")
			   .attr("x", function(d, i) { return i * (w / dataset.length); })
			   .attr("y", function(d) {	return h - (d * 50); })
			   .attr("width", w / dataset.length - barPadding)
			   .attr("height", function(d) { return d * 50; })
			   .attr("fill", function(d) { return "rgb(0, 0, " + (d * 35) + ")"; });

			svg.selectAll("text")
			   .data(dataset)
			   .enter()
			   .append("text")
			   .text(function(d) { return d; })
			   .attr("text-anchor", "middle")
			   .attr("x", function(d, i) {
					return i * (w / dataset.length) + (w / dataset.length - barPadding) / 2;
			   })
			   .attr("y", function(d) {	return h - (d * 50) + 14; })
			   .attr("font-family", "sans-serif")
			   .attr("font-size", "11px")
			   .attr("fill", "white");
		</script>
		
		<div class="container">
			<h4></h4>
			<table class="table table-striped" style="width:700px">
				<tbody>
					<tr>
						<td><b>Avg Cell Voltage:</b>3.58 V</td>
						<td><b>Highest Cell Voltage:</b>3.59 V</td>
						<td><b>Lowest Cell Voltage:</b>3.56 V</td>
						<td><b>Battery Pack Temperature:</b>20.5°C</td>
					</tr>
				</tbody>
			</table>
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
		</body>
</html>