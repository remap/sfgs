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
    <link rel="stylesheet" href="css/bootstrap.css">
	<style>	

		#playlist .padding-bottom label
		{
			display:inline-block;
			width:60px;
			text-align:right;
		}
		#loading_icon
		{
			text-align:center;
			margin-left:auto;
			margin-right:auto;
		}
		
		.update_message
		{
			text-align:center;
		}
		
		
		.container .video
		{
			width:240px;
			margin-bottom:-50px;
			padding-bottom:0px;
			text-align:center;
		}
		
		.container .video h3
		{
			font-size:18px;
			text-align:center;
			display:block;
		}
		.container .video h4
		{
			font-size:16px;
			text-align:center;
			margin-bottom:-20px;
			padding-bottom:0px;
			display:block;
		}
		
		.container p
		{
			display:block;
			width:250px;
			text-align:left;
			font-style:italic;
			font-size:14px;
		}
		
		.container .desc
		{
			font-size:16px;
		}
	</style>
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
          <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
          <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
        <![endif]-->
</head>

<body onLoad="return load_playlist();">
<?php  

	get_header();

?>

<nav class="navbar navbar-default">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1"> <span class="sr-only">Toggle navigation</span> <span class="icon-bar"></span> <span class="icon-bar"></span> <span class="icon-bar"></span></button>
      <a class="navbar-brand" href="<?php bloginfo('url') ?>"><?php bloginfo('name') ?></a></div>
    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <div><a href="../dashboard/" class="navbar-brand navbar-link padding-left">Dashboard<span class="sr-only">(current)</span></a></div>
      <div><a href="../collaboration" class="navbar-brand navbar-link padding-left">Profile</a></div>
      <div><a href="logout.php" class="navbar-brand navbar-link padding-left">Logout</a></div>
      <!--ul class="nav navbar-nav">
        <li class="active"> </li>
      </ul>
      <form class="navbar-form navbar-right" role="search">
        <div class="form-group"> </div>
      </form>
      <ul class="nav navbar-nav navbar-right">
        <li> </li>
        <li class="dropdown">
          <ul class="dropdown-menu" role="menu">
            <li><a href="#">Action</a></li>
            <li><a href="#">Another action</a></li>
            <li><a href="#">Something else here</a></li>
            <li class="divider"></li>
            <li><a href="#">Separated link</a></li>
          </ul>
        </li>
      </ul-->
    </div>
    <span class="active"></span>
    <!-- /.navbar-collapse -->
  </div>
  <!-- /.container-fluid -->
</nav>


<section>
    <div id="loading_icon" class="loading_icon">
        <img src="img/loading.gif"/>
    </div>
</section>

<section id="channel_meta">
	
</section>



<div id="playlist">
</div>

<hr>
<div class="section well">
  <div> </div>
</div>
<script src="js/jquery-1.11.2.min.js"></script> 
<script src="js/bootstrap.min.js"></script>

<?php get_footer(); ?>

</body>
</html>