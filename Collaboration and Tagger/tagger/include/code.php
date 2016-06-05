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
	
		
	//fetch YT tokens from Cassandras
	$user_email=$_SESSION['collab_user_email']; 
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
	
	
	$message='Invalid Access';
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
				 
				
		$method=$_GET['method'];
		$message='error';
		$API_key = 'AIzaSyAMHD0O136GOTAJcpMmiDXDQ2Vq5dp9b0o';
		
	
		switch($method)
		{
			case 'load_playlist':
				$query=$_GET['kw'];
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
//				}/*Youtube ends here*/

/*
				$nextpagetoken='';
				$index=0;
				$total=0;
				do
				{
					$current_set = json_decode(file_get_contents('https://www.googleapis.com/youtube/v3/search?order=date&part=snippet&channelId='.$_SESSION['channel_id'].'&maxResults=50&key='.$API_key.'&pageToken='.$nextpagetoken.''));
					$nextpagetoken=$current_set->nextPageToken;
					$video_list[]=$current_set;
					$total=$current_set->pageInfo->totalResults;
					if($total%50==0)
						$pages=$total/50;
					else	
						$pages=ceil(($total/50));
					$index++;	
							
				}while($index<$pages);
				
				
				foreach($video_list as $items)
				{
					foreach ($items->items as $item)
					{
							//Embed video
							if(isset($item->id->videoId))
							{
								$video_id[$count]=$item->id->videoId;
								$video_title[$count]=$item->snippet->title;
								$video_description[$count]=$item->snippet->description;
								$count++;
							}
						
					}
				}
				*/
			
				$message='';
				if($count==0)
				{
					echo '
					
					<section>	
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
				
				//Fetch from s4gs wp_emails table
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				
				$tags_updated_on = new ColumnFamily($pool, 'yt_video_updates');
				$vid_count=0;
				for($temp=0;$temp<$count;$temp++)
				{
					if($query!='')
					{
						if (preg_match('/'.$query.'/i', $video_title[$temp]))
							goto found;
						
						else if (preg_match('/'.$query.'/i', $video_description[$temp]))
							goto found;
						else
						  	continue;
						
					}
					found:
					$vid_count++;
					
					$last_updated=$tags_updated_on->get_count($video_id[$temp]);
					if($last_updated>0)
					{
						$last_updated_date=$tags_updated_on->get($video_id[$temp]);
						$last_updated=$last_updated_date['updated_on'];
					}
					else
						$last_updated='Never Updated';
						
					
					$message.='
					<section>	
						  <div class="container">
						  <table>
						  <tr>
						  <td>
							<div class="padding-left video">
							  <div>
								<h3><a href="https://www.youtube.com/watch?v='.$video_id[$temp].'" target="_blank">'.$video_title[$temp].'</a></h3>
								<h4>Video ID: '.$video_id[$temp].'</h4>
								<div class="videoThumb">
									<embed width="240" height="135" src="http://www.youtube.com/embed/'.$video_id[$temp].'">
								</div>
							  </div>
							</div>
							</td>
							<td width="25%" class="desc">
							<div class="padding-left">
							  <h4>Metadata Description:</h4><br/>
							  <p>'.$video_description[$temp].'</p>
							</div>
							</td>
							<td>
							<div class="padding-left">
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
						  <div class="padding-left">
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
									<button type="button" class="writeBtn" onClick="return update_tags(\''.$video_id[$temp].'\')">Write Metadata</button>
									</p>
							  <p>Last Update: <br/>'.$last_updated.'</p>
								<h5 id="'.$video_id[$temp].'_msg" class="update_message"></h5>
							 </div>
							 </td>
							 </tr>
							 </table>
							</div>	
						</section>	';
						
				}
				$_SESSION['video_count']=$vid_count;
				if ($vid_count<1)
					$message='No video found with searched string';
					$pool->close(); 
					$sys->close();
					goto finish;
				break;
				
				
			case 'load_channel_meta':
			
				$video_meta = json_decode(file_get_contents('https://www.googleapis.com/youtube/v3/channels?part=id%2Csnippet%2Cstatistics%2CcontentDetails%2CtopicDetails&id='.$_SESSION['channel_id'].'&key='.$API_key.''));
				


				foreach($video_meta->items as $item)
				{
					$_SESSION['channel_name'] = $item->snippet->title;
				}
					$message='
		<div class="container">
            <div class="row">
                <div class="col-xs12">
                    <h2>SFGS Metadata Tagger</h2>
                    <h3>Channel Name: <a target="_new" href="https://www.youtube.com/channel/'.$_SESSION['channel_id'].'">'.$_SESSION['channel_name'].'</a></h3>
                    <h3>Channel ID: '.$_SESSION['channel_id'].'</h3>
                    <h3>Total Videos: '.$_SESSION['video_count'].'</h3>
                </div>
      		</div>
    	</div>
	<br/>
	
					';
					goto finish;
				break;
				
			case 'update_tags':
			
			$id=$_GET['video_id'];
			$tag1=$_GET['tag1'];
			$tag2=$_GET['tag2'];
			$tag3=$_GET['tag3'];
			$tag4=$_GET['tag4'];
			$tag5=$_GET['tag5'];
			$tag6=$_GET['tag6'];
			$tag7=$_GET['tag7'];
			$chars=array();
			
			if($tag5!='')
				array_push($chars, $tag5);
			if($tag6!='')
				array_push($chars, $tag6);
			if($tag7!='')
				array_push($chars, $tag7);
				
			$desc = array(
			  'name' => $tag1,
			  'scene' => $tag2,
			  'shot' => $tag3,
			  'clip' => $tag4,
			  'characters'=> $chars
			);
			header('Content-type: text/javascript');
			
				if (isset($_SESSION['token'])) {
				  $client->setAccessToken($_SESSION['token']);
				} else {
				  $client->refreshToken($_SESSION['token']['refresh_token']);
				}
				// Check to ensure that the access token was successfully acquired.
				if ($client->getAccessToken()) {
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
			  $videoSnippet['description'] = json_encode($desc);
		
			  // Update the video resource by calling the videos.update() method.
			  $updateResponse = $youtube->videos->update("snippet", $video);
		
			  $responseTags = $updateResponse['snippet']['description'];
			  
			  //Store the update time in cassandra database
			  
					$cur_time=date('Y-m-d H:i:s');
					// Create a  new keyspace and column family
					$sys = new SystemManager('127.0.0.1');
					
					// Start a connection pool, create our ColumnFamily instance
					$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
					$update_video_table= new ColumnFamily($pool, 'yt_video_updates');
					$update_video_table->insert($videoId, array('updated_on' => $cur_time, 'updated_by' => $user_email, 'updated_tags' => json_encode($desc)));
					$pool->close(); 
					$sys->close();
			  //Store the update time in cassandra database ENDS
		
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
		unset($_SESSION['channel_name']);
		unset($_SESSION['channel_id']);
		unset($_SESSION['token']);
	finish:
	echo $message;
?>
