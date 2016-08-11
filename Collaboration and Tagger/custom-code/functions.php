<?php
session_start();
//error_reporting(E_ALL);
error_reporting(5);
date_default_timezone_set('America/Los_Angeles');
require_once(__DIR__.'/lib/autoload.php');
//include(__DIR__.'/../wp-includes/user.php');

use phpcassa\Connection\ConnectionPool;
use phpcassa\ColumnFamily;
use phpcassa\SystemManager;
use phpcassa\Schema\StrategyClass;
use phpcassa\ColumnSlice;
use phpcassa\Index\IndexExpression;
use phpcassa\Index\IndexClause;
$message='Invalid Access';

if(isset($_REQUEST['method']))
{
	$method=$_REQUEST['method'];
	
	switch($method)
	{
		case 'see_if_exists':
		
			break;
		case 'new_register':
		    
			$user_type='Registered';
			if(isset($_REQUEST['user_type']))
			{
				$user_type=$_REQUEST['user_type'];
			}
			$fn=$_REQUEST['fn'];
			$ln=$_REQUEST['ln'];
			$loc=$_REQUEST['loc'];
			$aff=$_REQUEST['aff'];
			$email1=$_REQUEST['email1'];
			$email2=$_REQUEST['email2'];
			$wp_email=$email1;
			if($user_type=='Registered')
			{
				$website=$_REQUEST['website'];
				$pass1=$_REQUEST['pass1'];
				$pass2=$_REQUEST['pass2'];
				$script_coverage=$_REQUEST['script_coverage'];
				$yt_url='';
				
			}
			else if ($user_type=='Guest')
			{
				$script_coverage=$_REQUEST['scene'];
				$yt_url=$_REQUEST['yt_url'];
				$website='';
				$pass1='';
				$pass2='';
			}
			$created_on=date('Y-m-d H:i:s');
			$ip=$_SERVER['REMOTE_ADDR'];
			$status='Applied';
			
			if(($user_type=='Registered')&&($fn=='' || $ln=='' || $loc=='' || $wp_email=='' || $aff=='' || $email1=='' || $email2=='' || $pass1=='' || $pass2==''))
			{
					$message='Fill all mandatory fields';
					goto finish;
			}
			else if ($user_type=='Guest'&&($fn=='' || $ln=='' || $loc=='' || $aff=='' || $email1=='' || $email2=='' || $script_coverage=='' || $yt_url==''))
			{
					$message='Fill all mandatory fields';
					goto finish;
			}
			else if($email1!=$email2)
			{
				$message='Emails do not match';
				goto finish;
			}			
			
			else if($pass1!=$pass2)
			{
				$message='Passwords do not match';
				goto finish;
			}
			
			else
			{
				
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				$add_user = new ColumnFamily($pool, 'users');
				$existing_email=$add_user->get_count($email1);
				// Check if email already exists
				if($existing_email>0)
				{
					$message='Email already in use';
					$pool->close(); 
					$sys->close();
					goto finish;
				}
				// Insert a record
				$add_user->insert($email1, array('aff' => $aff, 'created_by' => $wp_email, 'created_on' => $created_on, 'first_name' => $fn, 'last_name' => $ln, 'location' => $loc, 'password' => $pass1, 'ip' => $ip, 'script_progress' => 0, 'shots_count' => 0, 'status' => $status, 'videos_count' => 0, 'url_yt' => $yt_url, 'url_gplus' => '', 'gdrive' => '', 'updated_on' => $created_on, 'website' => $website, 'script_coverage' => $script_coverage, 'user_type' => $user_type));
				//Close our connections
				
				
				$add_user_wp= new ColumnFamily($pool, 'wp_emails');
				$existing_collab_email=$add_user_wp->get_count($email1);
				$add_user_wp->insert($wp_email, array('email' => $email1));
				$pool->close(); 
				
				$sys->close();
				
				$email='				
				<b>New form has been submitted for apprval</b><br/>
				<b>First Name:</b> '.$fn.'<br/>
				<b>Last Name:</b> '.$ln.'<br/>
				<b>Location:</b> '. $loc.'<br/>
				<b>Affiliation:</b> '. $aff.'<br/>
				<b>Email:</b> '. $email1.'<br/>
				<b>Created On:</b> '. $created_on.'<br/>
				<b>IP:</b> '. $ip.'<br/>
				<b>Account Status:</b> '. $status.'<br/>
				<b>Created By User:</b> '. $wp_email.'<br/>
				
				<a href="http://searchforglobalsong.com/author/index.php/collaboration-users/?action=changeStatus&email='.$email1.'&status=Approved">Approve</a>
				 
				<a href="http://searchforglobalsong.com/author/index.php/collaboration-users/?action=changeStatus&email='.$email1.'&status=Denied">Deny </a>
				<p>You need to login with administrator account to approve or deny the request.</p>
				';
				
				
				$to = 'search4global@gmail.com';
				$subject = 'New Reigstration For Channel';
				
					
				$headers = 'From: no-reply@remap.ucla.edu'. "\r\n";
				$headers .= "MIME-Version: 1.0\r\n";
				$headers .= "Content-Type: text/html; charset=ISO-8859-1\r\n";

				// Can do no-reply@remap.ucla.edu, or the-archive@remap.ucla.edu
				// Can't do without -f specification
				if (mail($to,$subject,$email,$headers)) 
				{
					$message='success';
					goto finish;
				} 
				else 
				{
				  $message="emailfailed";
					goto finish;
				}				
				
			}

			break;
		case 'collab_login':
		
				$email=$_REQUEST['email'];
				$password=$_REQUEST['pass'];
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				$check_user = new ColumnFamily($pool, 'users');
				$existing_email=$check_user->get_count($email);
				// Check if email already exists
				if($existing_email<1)
				{
					$message='Email not found';
					$pool->close(); 
					$sys->close();	
					goto finish;
				}
					$user_details=$check_user->get($email);
					if($password==$user_details['password'])
					{
						$_SESSION['collab_user']=$user_details;
						$_SESSION['collab_user_email']=$email;
						
						$message='success';
					}
					else
					{
						$message='Invalid Password';
					}
				$pool->close(); 
				$sys->close();	
			break;
			
			
		case 'reset_pass':
		
				$email=$_REQUEST['email'];
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				$check_user = new ColumnFamily($pool, 'users');
				$existing_email=$check_user->get_count($email);
				// Check if email already exists
				if($existing_email<1)
				{
					$message='Email not found';
					$pool->close(); 
					$sys->close();	
					goto finish;
				}
					$new_pass = substr(hash('sha512',rand()),6,8);
					$check_user->insert($email, array('password' => $new_pass));
					
					$to = $email;
					$subject = 'New Password For S4GS';
					
						
					$headers = 'From: no-reply@remap.ucla.edu'. "\r\n";
					$headers .= "MIME-Version: 1.0\r\n";
					$headers .= "Content-Type: text/html; charset=ISO-8859-1\r\n";
					$body='<br/>New password for S4GS user <b>'.$email.'</b> is: <i>'.$new_pass.'</i>';
	
					// Can do no-reply@remap.ucla.edu, or the-archive@remap.ucla.edu
					// Can't do without -f specification
					if (mail($to,$subject,$body,$headers)) 
					{
						$message='success';
						goto finish;
					} 
					else 
					{
					  $message="emailfailed";
						goto finish;
					}
					
				$pool->close(); 
				$sys->close();	
			break;
			
		case 'update':
		if(!$_SESSION['collab_user_email'])
		{
			$message='Session Expired. Please Login Again.';
				goto finish;
		}
			$fn=$_REQUEST['fn'];
			$ln=$_REQUEST['ln'];
			$loc=$_REQUEST['loc'];
			$aff=$_REQUEST['aff'];
			$email1=$_REQUEST['email1'];
			$email2=$_REQUEST['email2'];
			$website=$_REQUEST['website'];
			$current_pass1=$_REQUEST['current_pass1'];
			$wp_email=$_SESSION['collab_user_email'];
			$script_coverage=$_REQUEST['script_coverage'];
			
		//$pass1=$_REQUEST['pass1'];
			//$pass2=$_REQUEST['pass2'];
			$updated_on=date('Y-m-d H:i:s');
			$ip=$_SERVER['REMOTE_ADDR'];
			
			
			if($fn=='' || $ln=='' || $loc=='' || $aff=='' || $wp_email=='' || $email1=='' || $email2=='' || $current_pass1=='')
			{
				$message='Fill all mandatory fields';
				goto finish;
			}
			else if($email1!=$email2)
			{
				$message='Emails do not match';
				goto finish;
			}
			
			else if($pass1!=$pass2)
			{
				$message='Passwords do not match';
				goto finish;
			}
			
			else
			{//fetch emailid from wp_user table
				
				//Fetch from s4gs wp_emails table
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				
				$exist_user = new ColumnFamily($pool, 'wp_emails');
				$add_user = new ColumnFamily($pool, 'users');
				$existing_emails=$exist_user->get_count($wp_email);
				$existing_wp_table=$exist_user->get($wp_email);
					
					
								
				if($existing_emails<1)
				{
					$message='Seems like you donot have an account in system. Please contact admin if you already had.';
					goto finish;
				}
				
				
				
				
				$existing_email=$add_user->get_count($email1);
							
				$existing_user_details=$add_user->get($existing_wp_table['email']);
				
				// Check if email already exists
				if($existing_email>0 && ($existing_wp_table['email']!=$email1))
				{
					$message='Email already in use';
					$pool->close(); 
					$sys->close();
					goto finish;
				}
				
				
						
				// Check Current password
				if($existing_user_details['password']!=$current_pass1)
				{
					$message='Incorrect Current Password';
					$pool->close(); 
					$sys->close();
					goto finish;
				}
				if($existing_wp_table['email']!=$email1)
				{
					//Fetch from s4gs wp_emails table
					// Create a  new keyspace and column family
					// Start a connection pool, create our ColumnFamily instance
					$add_user->remove($existing_wp_table['email']);
					
					$add_user->insert($email1, array('aff' => $aff, 'updated_on' => $updated_on, 'first_name' => $fn, 'last_name' => $ln, 'location' => $loc, 'ip' => $ip, 'website' => $website, 'created_by' => $existing_user_details['created_by'], 'created_on' => $existing_user_details['created_on'], 'script_progress' => $existing_user_details['script_progress'], 'shots_count' => $existing_user_details['shots_count'], 'status'=>$existing_user_details['status'], 'url_gplus'=>$existing_user_details['url_gplus'], 'url_yt'=>$existing_user_details['url_yt'], 'gdrive'=>$existing_user_details['gdrive'], 'videos_count'=>$existing_user_details['videos_count'], 'password'=>$existing_user_details['password'], 'script_coverage'=>$existing_user_details['script_coverage']));
				
					$exist_user->insert($wp_email, array('email' => $email1)); //update wp_table
				}
				else
				{
					$add_user->insert($email1, array('aff' => $aff, 'updated_on' => $updated_on, 'first_name' => $fn, 'last_name' => $ln, 'location' => $loc, 'ip' => $ip, 'website' => $website, 'script_coverage' => $script_coverage));
				}
				
				$pool->close(); 
				
				$sys->close();
				$message='success';		
				
			}

			break;
		
		
		case 'updateByAdmin':
			$fn=$_REQUEST['fn'];
			$ln=$_REQUEST['ln'];
			$loc=$_REQUEST['loc'];
			$aff=$_REQUEST['aff'];
			$email=$_REQUEST['email'];
			$wp_email=$_REQUEST['wp_email'];
			$website=$_REQUEST['website'];
			$url_gplus=$_REQUEST['url_gplus'];
			$url_yt=$_REQUEST['url_yt'];
			$gdrive=$_REQUEST['gdrive'];
			$videos_count=$_REQUEST['videos_count'];
			$script_coverage=$_REQUEST['script_coverage'];
			$script_progress=$_REQUEST['script_progress'];
			$shots_count=$_REQUEST['shots_count'];
			
		//$pass1=$_REQUEST['pass1'];
			//$pass2=$_REQUEST['pass2'];
			$updated_on=date('Y-m-d H:i:s');
			$ip=$_SERVER['REMOTE_ADDR'];
			
			
			/*if($fn=='' || $ln=='' || $loc=='' || $aff=='' || $wp_email=='' || $email=='' || $email2=='' || $current_pass1=='')
			{
				$message='Fill all mandatory fields';
				goto finish;
			}*/
			
			
			{//fetch emailid from wp_user table
				
				//Fetch from s4gs wp_emails table
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				
				$exist_user = new ColumnFamily($pool, 'wp_emails');
				$add_user = new ColumnFamily($pool, 'users');
				$existing_emails=$exist_user->get_count($wp_email);
				$existing_wp_table=$exist_user->get($wp_email);
					
								
				if($existing_emails<1)
				{
					$message='Seems like you donot have an account in system. Please contact admin if you already had.';
					goto finish;
				}
				
				$existing_email=$add_user->get_count($email);
				$existing_user_details=$add_user->get($existing_wp_table['email']);
				// Check if email already exists
				if($existing_email>0 && $existing_wp_table['email']!=$email)
				{
					$message='Email already in use';
					$pool->close(); 
					$sys->close();
					goto finish;
				}
				
				
				/*
						
				No need to Check Current password
				if($existing_user_details['password']!=$current_pass1)
				{
					$message='Incorrect Current Password';
					$pool->close(); 
					$sys->close();
					goto finish;
				}*/
				if($existing_wp_table['email']!=$email)
				{
					//Fetch from s4gs wp_emails table
					// Create a  new keyspace and column family
					// Start a connection pool, create our ColumnFamily instance
					$add_user->remove($existing_wp_table['email']);
					$exist_user->insert($wp_email, array('email' => $email)); //update wp_table
					$add_user->insert($email, array('aff' => $aff, 'updated_on' => $updated_on, 'first_name' => $fn, 'last_name' => $ln, 'location' => $loc, 'password' => $existing_user_details['password'], 'ip' => $ip, 'website' => $website, 'created_by' => $existing_user_details['created_by'], 'created_on' => $existing_user_details['created_on'], 'url_gplus' => $url_gplus, 'url_yt' => $url_yt, 'script_coverage' => $script_coverage, 'gdrive' => $gdrive, 'videos_count' => $videos_count, 'script_progress' => $script_progress, 'shots_count' => $shots_count, 'status' => $existing_user_details['status']));
					 
				}
				else
				{
					$add_user->insert($email, array('aff' => $aff, 'updated_on' => $updated_on, 'first_name' => $fn, 'last_name' => $ln, 'location' => $loc, 'ip' => $ip, 'website' => $website, 'url_gplus' => $url_gplus, 'url_yt' => $url_yt, 'script_coverage' => $script_coverage, 'gdrive' => $gdrive, 'videos_count' => $videos_count, 'script_progress' => $script_progress,  'shots_count' => $shots_count));
				}
				
				$pool->close(); 
				
				$sys->close();
				$message='success';		
				
			}

			break;
		
		
		case 'change_password':
		if(!$_SESSION['collab_user_email'])
		{
			$message='Session Expired. Please Login Again.';
				goto finish;
		}
			$current_pass=$_REQUEST['current_pass'];
			$new_pass1=$_REQUEST['new_pass1'];
			$new_pass2=$_REQUEST['new_pass2'];
			$wp_email=$_SESSION['collab_user_email'];
		//$pass1=$_REQUEST['pass1'];
			//$pass2=$_REQUEST['pass2'];
			$updated_on=date('Y-m-d H:i:s');
			$ip=$_SERVER['REMOTE_ADDR'];
			
			
			if($current_pass=='' || $new_pass1=='' || $new_pass2=='')
			{
				$message='Fill all mandatory fields';
				goto finish;
			}
			else if($new_pass1!=$new_pass2)
			{
				$message='New and Confirm Passwords do not match';
				goto finish;
			}
			
			else
			{//fetch emailid from wp_user table
				
				//Fetch from s4gs wp_emails table
				// Create a  new keyspace and column family
				$sys = new SystemManager('127.0.0.1');
				// Start a connection pool, create our ColumnFamily instance
				$pool = new ConnectionPool('s4gs', array('127.0.0.1'));
				
				$exist_user = new ColumnFamily($pool, 'wp_emails');
				$add_user = new ColumnFamily($pool, 'users');
				$existing_emails=$exist_user->get_count($wp_email);
				$existing_wp_table=$exist_user->get($wp_email);
					
					
								
				if($existing_emails<1)
				{
					$message='Seems like you donot have an account in system. Please contact admin if you already had.';
					goto finish;
				}
				
							
				$existing_user_details=$add_user->get($existing_wp_table['email']);
				
										
				// Check Current password
				if($existing_user_details['password']!=$current_pass)
				{
					$message='Incorrect Current Password';
					$pool->close(); 
					$sys->close();
					goto finish;
				}
				$add_user->insert($existing_wp_table['email'], array('password' => $new_pass1));
								
				$pool->close(); 
				
				$sys->close();
				$message='success';		
				
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
