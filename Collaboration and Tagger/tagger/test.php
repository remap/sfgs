<?php
	session_start();
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
	
		
	//fetch YT tokens from Cassandras
	$user_email='balramverma@gmail.com';
	$_SESSION['loggedin_user']=$user_email; 
	function fetch_yttoken($username)	
	{
	
		//Fetch from s4gs wp_emails table
		// Create a  new keyspace and column family
		$sys = new SystemManager('127.0.0.1');
		// Start a connection pool, create our ColumnFamily instance
		$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
		
		$YTtoken_qry = new ColumnFamily($pool, 'yttokens');
		if($YTtoken_qry->get_count($username)>0)
			$YTtoken=$YTtoken_qry->get($username);
		else
			$YTtoken='no user';
		$pool->close(); 
		
		$sys->close();
		return($YTtoken);
	}
	
	
					$token=fetch_yttoken($user_email);
					if($token=='no user')
					{
						$message='Youtube account not found for user '.$user_email;
						goto finish;
					}
					else
					{
						$stored_token=array('access_token'=>$token['access_token'], 'token_type'=>$token['token_type'], 'expires_in'=>$token['expires_in'], 'refresh_token'=>$token['refresh_token'], 'created'=>$token['created']);
						
						$_SESSION['token']=array('access_token'=>$token['access_token'], 'token_type'=>$token['token_type'], 'expires_in'=>$token['expires_in'], 'refresh_token'=>$token['refresh_token'], 'created'=>$token['created']);
					}
				$count=0;
				//Youtube code		-------------------------------//	
				$OAUTH2_CLIENT_ID = '1005921410437-eddlq86k4197k4ev03p7cc0jtitla7pi.apps.googleusercontent.com';
				$OAUTH2_CLIENT_SECRET = 'BsZP32xNHKTeJ_jA4alf2-8U';
				
				$client = new Google_Client();
				$client->setClientId($OAUTH2_CLIENT_ID);
				$client->setClientSecret($OAUTH2_CLIENT_SECRET);
				$client->setScopes('https://www.googleapis.com/auth/youtube');
				$client->setAccessType('offline');
				$redirect = filter_var('http://' . $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'],
				  FILTER_SANITIZE_URL);
				$client->setRedirectUri($redirect);

				 
				// Define an object that will be used to make all API requests.
				$youtube = new Google_Service_YouTube($client);
				 
		$message='error';
		$_SESSION['channel_id'] = $token['channel_id'];
		$API_key = 'AIzaSyAMHD0O136GOTAJcpMmiDXDQ2Vq5dp9b0o';
		

			
				// Check to ensure that the access token was successfully acquired.
				//if ($client->getAccessToken()) {
					
					
						//if($client->isAccessTokenExpired()) {
							//echo "expired!";
							//Fetch new token if expired
							//$newToken = json_decode($client->getAccessToken());
						
						// Define an object that will be used to make all API requests.
						$youtube = new Google_Service_YouTube($client);
						
						
						//$_SESSION['token']=array('access_token'=>'ya29.pgJUVElqYX2bA7LpjV9Twobo9cY3hJYrvwa1joW8X_bMo2wO4tOI7epdfPBNj3M9kQ', 'token_type'=>'Bearer', 'expires_in'=>'3600', 'refresh_token'=>'1/GPYEHxm8nyblX3N-SHrikDWl1p-2exBy9-KTMz8_fjoMEudVrK5jSpoR30zcRFq6', 'created'=>'1458025178');
						if (isset($_SESSION['token'])) {
						  $client->setAccessToken($_SESSION['token']);
						} /*else {
						  $client->refreshToken($_SESSION['token']['refresh_token']);
						}*/
						// Check to ensure that the access token was successfully acquired.
						if ($client->getAccessToken()) {
						  try {
							// Call the channels.list method to retrieve information about the
							// currently authenticated user's channel.
							$channelsResponse = $youtube->channels->listChannels('contentDetails', array(
							  'mine' => 'true',
							));
						
							$htmlBody = '';
							foreach ($channelsResponse['items'] as $channel) {
							  // Extract the unique playlist ID that identifies the list of videos
							  // uploaded to the channel, and then call the playlistItems.list method
							  // to retrieve that list.
							  $uploadsListId = $channel['contentDetails']['relatedPlaylists']['uploads'];
						
							  $playlistItemsResponse = $youtube->playlistItems->listPlaylistItems('snippet', array(
								'playlistId' => $uploadsListId,
								'maxResults' => 50
							  ));
						
							  
								foreach ($playlistItemsResponse['items'] as $playlistItem) 
								{
									$_SESSION['channel_id']=$playlistItem['snippet']['channelId'];
									$_SESSION['channel_name']=$playlistItem['snippet']['channelTitle'];
									$video_id[$count]=$playlistItem['snippet']['resourceId']['videoId'];
									$video_title[$count]=$playlistItem['snippet']['title'];
									$video_description[$count]=$playlistItem['snippet']['description'];
									$count++;
									
									echo '<br/>'.$playlistItem['snippet']['title'].' '.$playlistItem['snippet']['resourceId']['videoId'];
								}
							}
						  } catch (Google_Service_Exception $e) {
							$htmlBody .= sprintf('<p>A service error occurred: <code>%s</code></p>',
							  htmlspecialchars($e->getMessage()));
						  } catch (Google_Exception $e) {
							$htmlBody .= sprintf('<p>An client error occurred: <code>%s</code></p>',
							  htmlspecialchars($e->getMessage()));
						  }
						
						  $_SESSION['token'] = $client->getAccessToken();
						}
						
				$message='';
				$_SESSION['video_count']=$count;
				if($count==0)
				{
					echo '
					
					<section>					
						<hr>
						  <div class="container">
							<div class="col-lg-2.5 padding-left padding-bottom video">
							  <div>
							  	<p>No Public Video Found</p>
							  </div>
							 </div>
						  </div>
					</section>
					';
				}
				for($temp=0;$temp<$count;$temp++)
				{
					$message.='
					<section>					
						<hr>
						  <div class="container">
							<div class="col-lg-2.5 padding-left padding-bottom video">
							  <div>
								<h3 class="col-lg-11">'.$video_title[$temp].'</h3>
								<h4>Video ID: <a href="https://www.youtube.com/watch?v='.$video_id[$temp].'" target="_blank">'.$video_id[$temp].'</a></h4>
								<h1 class="col-lg-11">
									<div>
										<embed width="240" height="135" src="http://www.youtube.com/embed/'.$video_id[$temp].'">
									</div>
								</h1>
							  </div>
							</div>
							<div class="col-lg-2.5 padding-left padding-top">
							  <h4>Metadata Description:</h4>
							  <p class="desc">'.$video_description[$temp].'</p>
							</div>
							<div> </div>
							<div class="padding-left padding-top col-lg-2.5">
								<div class="padding-bottom">
						  <label for="'.$video_id[$temp].'_txt1">Name :</label>
							<input type="text" name="'.$video_id[$temp].'_txt1" id="'.$video_id[$temp].'_txt1">
						  &nbsp;</div>
						  <div class="padding-bottom">
						  <label for="'.$video_id[$temp].'_txt2">Scene :</label>
							<input type="text" name="'.$video_id[$temp].'_txt2" id="'.$video_id[$temp].'_txt2">
						  &nbsp;</div>
						  <div class="padding-bottom">
							<label for="'.$video_id[$temp].'_txt3">Shot : </label>
							 <input type="text" name="'.$video_id[$temp].'_txt3" id="'.$video_id[$temp].'_txt3">
						  &nbsp;</div>
						  <div class="padding-bottom">
							<label for="'.$video_id[$temp].'_txt4">Clip : </label>
							<input type="text" name="'.$video_id[$temp].'_txt4" id="'.$video_id[$temp].'_txt4">
						  &nbsp;</div>
							</div>
						  <div class="col-lg-1 padding-top padding-left">
						  <table width="200">
							<tr>
							  <td><label>
								<input type="checkbox" value="Fern" name="'.$video_id[$temp].'_chk1" id="'.$video_id[$temp].'_chk1">
								Fern</label></td>
							</tr>
							<tr> <td><label>
								<input type="checkbox" value="Masha" name="'.$video_id[$temp].'_chk2" id="'.$video_id[$temp].'_chk2">
								Masha</label></td></tr>
							<tr>
							  <td><label>
								<input type="checkbox" value="Samuel" name="'.$video_id[$temp].'_chk3" id="'.$video_id[$temp].'_chk3">
								Samuel</label></td>
							</tr>
							</table>
							</div>
							<div class="padding-top col-lg-2 padding-left">
							  <p>
									<button type="button" class="btn btn-primary btn-lg" onClick="return update_tags(\''.$video_id[$temp].'\')">Write Metadata</button>
									</p>
							  <p>Date of update</p>
								<h5 id="'.$video_id[$temp].'_msg" class="update_message"></h5>
							 </div>
							</div>	
						</section>	';
				}
				
	finish:
?>
