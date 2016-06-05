<?php
	session_start();
	//require_once('conn.php');
	
	//error_reporting(E_ALL);
	//error_reporting(5);
	date_default_timezone_set('America/Los_Angeles');
	require_once('../../custom-code/lib/autoload.php');
	
	//include(__DIR__.'/../wp-includes/user.php');
	
	use phpcassa\Connection\ConnectionPool;
	use phpcassa\ColumnFamily;
	use phpcassa\SystemManager;
	use phpcassa\Schema\StrategyClass;
	use phpcassa\ColumnSlice;
	use phpcassa\Index\IndexExpression;
	use phpcassa\Index\IndexClause;
	
	
	// Call set_include_path() as needed to point to your client library.
	require_once '../google-api-php-client/vendor/autoload.php';
	require_once '../google-api-php-client/src/Google/Client.php';
	require_once '../google-api-php-client/src/Google/Service/YouTube.php';
	
		
	//fetch YT tokens from Cassandra			
	$user='galobal';
	function fetch_yttoken($username)
	{
	
		//Fetch from s4gs wp_emails table
		// Create a  new keyspace and column family
		$sys = new SystemManager('127.0.0.1');
		// Start a connection pool, create our ColumnFamily instance
		$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
		
		$YTtoken_qry = new ColumnFamily($pool, 'yttokens');
		$YTtoken=$YTtoken_qry->get($username);
		
		$pool->close(); 
		
		$sys->close();
		return($YTtoken);
	}
	
	
	$message='Invalid Access';
	
	if(isset($_REQUEST['method']))
	{
				$token=fetch_yttoken($user);
				$count=0;
				//Youtube code		-------------------------------//			
				$OAUTH2_CLIENT_ID = '799629813172-dpb2c21vvv8gonso7krrf2s5rs60t88v.apps.googleusercontent.com';
				$OAUTH2_CLIENT_SECRET = 'WKKqBtcfpHz7AUhu_0VFevmh';
				$REDIRECT = filter_var('http://' . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'], FILTER_SANITIZE_URL);
				//$REDIRECT = 'http://searchforglobalsong.com/author/tagger/test.php';
				
				
				$APPNAME = "S4GS Authentication";
				 
				$client = new Google_Client();
				$client->setClientId($OAUTH2_CLIENT_ID);
				$client->setClientSecret($OAUTH2_CLIENT_SECRET);
				$client->setScopes('https://www.googleapis.com/auth/youtube');
				$client->setRedirectUri($REDIRECT);
				$client->setApplicationName($APPNAME);
				$client->setAccessType('offline');
				$client->setAccessToken(array("access_token"=>$token['access_token'],"token_type"=>$token['token_type'],"expires_in"=>$token['expires_in'],"refresh_token"=>$token['refresh_token'],"created"=>$token['created']));
				 
				// Define an object that will be used to make all API requests.
				$youtube = new Google_Service_YouTube($client);
				 
				
		$method=$_REQUEST['method'];
		$message='error';
		switch($method)
		{
			case 'load_playlist':
				// Check to ensure that the access token was successfully acquired.
				if ($client->getAccessToken()) {
					
					
						if($client->isAccessTokenExpired()) {
							//Fetch new token if expired
							$newToken = json_decode($client->getAccessToken());
							$client->refreshToken($newToken->refresh_token);
							$new_token=$client->getAccessToken();
				
						}
				 
						$youtube = new Google_Service_YouTube($client);
					try {
						// Call the channels.list method to retrieve information about the
						// currently authenticated user's channel.
						$channelsResponse = $youtube->channels->listChannels('contentDetails', array(
							'mine' => 'true',
						));
				 
						foreach ($channelsResponse['items'] as $channel) {
							// Extract the unique playlist ID that identifies the list of videos
							// uploaded to the channel, and then call the playlistItems.list method
							// to retrieve that list.
							$uploadsListId = $channel['contentDetails']['relatedPlaylists']['uploads'];
				 
							$playlistItemsResponse = $youtube->playlistItems->listPlaylistItems('snippet', array(
								'playlistId' => $uploadsListId
							));
				 			
							foreach ($playlistItemsResponse['items'] as $playlistItem) 
							{
								$video_id[$count]=$playlistItem['snippet']['resourceId']['videoId'];
								$video_title[$count]=$playlistItem['snippet']['title'];
								$count++;
							}
						}
					} catch (Google_ServiceException $e) {
						$message .= sprintf('<p>A service error occurred: <code>%s</code></p>',
							htmlspecialchars($e->getMessage()));
					} catch (Google_Exception $e) {
						$message .= sprintf('<p>An client error occurred: <code>%s</code></p>',
							htmlspecialchars($e->getMessage()));
					}
				 	
					$_SESSION['token'] = $client->getAccessToken();
				
				}/*Youtube ends here*/
				$message='';
				$_SESSION['video_count']=$count;
				for($temp=0;$temp<$count;$temp++)
				{
					
									
				$message.='
							<section>
							  <div class="container">
								<div class="row">
								  <div class="col-md-6 text-center">
									<h3>'.$video_title[$temp].'</h3>
								  </div>';
								  if($video_title[$temp+1]!='')
								  {
							$message.='
								  <div class="col-md-6 text-center">
									<h3>'.$video_title[$temp+1].'<br>
									</h3>
								  </div>';
								  }
								
							$message.='</div>
								<div class="row">
									<div class="col-md-3 text-center">
									  	<div><embed width="240" height="135" src="http://www.youtube.com/embed/'.$video_id[$temp].'">
										</div>
									</div>
									<div class="col-md-3 padding-left padding-right">
									  <label for="'.$video_id[$temp].'_txt1">Scene:</label>
									  <input type="text" name="'.$video_id[$temp].'_txt1" id="'.$video_id[$temp].'_txt1">
									  <label for="'.$video_id[$temp].'_txt2">Shot:</label>
									  <input type="text" name="'.$video_id[$temp].'_txt2" id="'.$video_id[$temp].'_txt2">
									  <label for="'.$video_id[$temp].'_txt3">Clip:</label>
									  <input type="text" name="'.$video_id[$temp].'_txt3" id="'.$video_id[$temp].'_txt3">
                						
									  <div class="float-left">
									  </div>
									  
									<button type="button" class="btn-primary btn" onClick="return update_tags(\''.$video_id[$temp].'\')">UPDATE TAGS</button>
									<h5 id="'.$video_id[$temp].'_msg"></h5>
								  </div>';
							  if($video_id[$temp+1]!='')
							  {
						$message.='
								  
						<div class="col-md-3 text-center col-sm-6 col-xs-6 hidden-xs hidden-sm">
							<embed width="240" height="135" src="http://www.youtube.com/embed/'.$video_id[++$temp].'">										
						</div>
						<div class="col-md-3 padding-top padding-right padding-left">
							  <label for="'.$video_id[$temp].'_txt1">Scene:</label>
							  <input type="text" name="'.$video_id[$temp].'_txt1" id="'.$video_id[$temp].'_txt1">
							  <label for="'.$video_id[$temp].'_txt2">Shot:</label>
							  <input type="text" name="'.$video_id[$temp].'_txt2" id="'.$video_id[$temp].'_txt2">
							  <label for="'.$video_id[$temp].'_txt3">Clip:</label>
							  <input type="text" name="'.$video_id[$temp].'_txt3" id="'.$video_id[$temp].'_txt3">
						  <div>
						  </div>
									<button type="button" class="btn-primary btn" onClick="return update_tags(\''.$video_id[$temp].'\')">UPDATE TAGS</button>
                			<h5 id="'.$video_id[$temp].'_msg"></h5>
						</div>
						</div>
						<hr>';
							  }
				  $message.='
					  </div>
					</section>';
				}
					goto finish;
				break;
				
				
			case 'load_channel_meta':
					$message='
					
						<section class="col-lg-12">
						  <div class="well">
						<h3><em>'.$_SESSION['video_count'].' videos</em></h3>
							<p>last updated 2/17/16</p>
						  </div>
						</section>
					';
					goto finish;
				break;
				
			case 'update_tags':
			$id=$_GET['video_id'];
			$desc=$_GET['description'];
				// Check to ensure that the access token was successfully acquired.
				if ($client->getAccessToken()) {
					
					
						if($client->isAccessTokenExpired()) {
							$newToken = json_decode($client->getAccessToken());
							$client->refreshToken($newToken->refresh_token);
							$new_token=$client->getAccessToken();
							//Fetch from s4gs wp_emails table
							// Create a  new keyspace and column family
							$sys = new SystemManager('127.0.0.1');
							// Start a connection pool, create our ColumnFamily instance
							$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
							
							$YTtoken_qry = new ColumnFamily($pool, 'yttokens');
							$YTtoken_qry->insert($user, array('access_token' => $new_token['access_token'],'token_type' => $new_token['token_type'],'expires_in' => $new_token['expires_in'] ,'refresh_token' => $new_token['refresh_token'] , 'created' => $new_token['created']));
							
							$pool->close(); 
							
							$sys->close();
						}
				 
						$youtube = new Google_Service_YouTube($client);
					try {
								
			// REPLACE this value with the video ID of the video being updated.
			$videoId = $id;
		
			// Call the API's videos.list method to retrieve the video resource.
			$listResponse = $youtube->videos->listVideos("snippet",
				array('id' => $videoId));
		
			// If $listResponse is empty, the specified video was not found.
			if (empty($listResponse)) {
			  $message .= sprintf('<h3>Can\'t find a video with video id: %s</h3>', $videoId);
			} else {
			  // Since the request specified a video ID, the response only
			  // contains one video resource.
			  $video = $listResponse[0];
			  $videoSnippet = $video['snippet'];
			  $tags = $videoSnippet['description'];
			  // Preserve any tags already associated with the video. If the video does
			  // not have any tags, create a new list. Replace the values "tag1" and
			  // "tag2" with the new tags you want to associate with the video.
		
			  // Set the tags array for the video snippet
			  $videoSnippet['description'] = $desc;
		
			  // Update the video resource by calling the videos.update() method.
			  $updateResponse = $youtube->videos->update("snippet", $video);
		
			  $responseTags = $updateResponse['snippet']['description'];
		
		
			$message= 'updated';
		  }
			} catch (Google_Service_Exception $e) {
			  $message .= sprintf('<p>A service error occurred: <code>%s</code></p>',
				  htmlspecialchars($e->getMessage()));
			} catch (Google_Exception $e) {
			  $message .= sprintf('<p>An client error occurred: <code>%s</code></p>',
				  htmlspecialchars($e->getMessage()));
			}
		
			$_SESSION['token'] = $client->getAccessToken();
			} 
				break;
			
			default:
				$message='invalid request';			
				break;
		}
	}
	finish:
	echo $message;
?>