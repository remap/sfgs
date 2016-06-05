<?php		

	//error_reporting(E_ALL);
	//error_reporting(5);
	session_start();
	if(!isset($_SESSION['collab_user']))
	{
		header('location:../collaboration-login/');
	}

	date_default_timezone_set('America/Los_Angeles');
	require_once('../custom-code/lib/autoload.php');
	
	use phpcassa\Connection\ConnectionPool;
	use phpcassa\ColumnFamily;
	use phpcassa\SystemManager;
	use phpcassa\Schema\StrategyClass;
	use phpcassa\ColumnSlice;
	use phpcassa\Index\IndexExpression;
	use phpcassa\Index\IndexClause;
	
	
	// Call set_include_path() as needed to point to your client library.
	require_once 'google-api-php-client/vendor/autoload.php';
	require_once 'google-api-php-client/src/Google/Client.php';
	require_once 'google-api-php-client/src/Google/Service/YouTube.php';
	
	require_once('../wp-load.php');	
  

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
	<title>SFGS Metadata Tagger</title>
    
    <script src="include/script.js"></script>
    <link rel="stylesheet" href="css/style.css">
	<style>	

		
	</style>
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
          <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
          <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
        <![endif]-->
</head>

<body onLoad="return load_playlist('load');">
<?php  

	get_header();

?>

<nav class="navbar navbar-default">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header" >
      <a class="navbar-brand" href="../collaboration">Profile</a>
      <a class="navbar-brand" href="logout.php">Logout</a></div>
      </div>
    <!-- Collect the nav links, forms, and other content for toggling -->
    <!--div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <div><a href="../collaboration" class="navbar-brand navbar-link padding-left">Profile</a></div>
      <div><a href="logout.php" class="navbar-brand navbar-link padding-left">Logout</a></div>
      
  </div-->
  <!-- /.container-fluid -->
</nav>



<section id="channel_meta">
	
</section>


<section class="search_box" id="search_panel">
            <input type="text"  placeholder="Search" name="search_box" id="search_box"/>	
            <button type="submit" class="btn btn-default btn-primary" onClick="return load_playlist('search');">Search </button>
</section>


<section>
    <div id="loading_icon" class="loading_icon">
        <img src="img/loading.gif"/>
    </div>
</section>

<div id="playlist">
</div>
<div class="section well">
  <div> </div>
</div>
<script src="js/jquery-1.11.2.min.js"></script> 
<script src="js/bootstrap.min.js"></script>

<?php get_footer(); ?>

</body>
</html>