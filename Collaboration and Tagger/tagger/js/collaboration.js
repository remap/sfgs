/** JS**/
function register()
{
	
	var fn=document.getElementById('fname').value;
	var ln=document.getElementById('lname').value;
	var loc=document.getElementById('location').value;
	var aff=document.getElementById('affiliation').value;
	var email1=document.getElementById('email').value;
	var email2=document.getElementById('reemail').value;
	var website=document.getElementById('website').value;
	var pass1=document.getElementById('pass').value;
	var pass2=document.getElementById('confpass').value;
	var term=document.getElementById('termchk').checked;
	var wp_email=document.getElementById('wp_email').value;
	var script_coverage=document.getElementById('script_coverage').value;
	
	if(term==true)
	{
			var xhttp = new XMLHttpRequest();
			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xhttp = new XMLHttpRequest();
			} else {
				// code for IE6, IE5
				xhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xhttp.onreadystatechange = function() 
			{
				if (xhttp.readyState == 4 && xhttp.status == 200) 
				{
					var response= xhttp.responseText;
					if(response=='success')
					{
						location.reload();
						return false;
					}
					if(response=='emailfailed')
					{
						document.getElementById('reg_form').style.display='none';
						document.getElementById('success_msg').innerHTML='Form has been submitted. Email sending failed';
						document.getElementById('error_msg').style.display='none';
						return false;
					}
					else
					{
						document.getElementById('error_msg').style.display='block';
						document.getElementById('error_msg').innerHTML=xhttp.responseText;
						document.getElementById('form_submit').style.display='block';
						document.getElementById('form_sending').style.display='none';
						scroll('error_msg');
						return false;
					}
				}
				if(xhttp.readyState == 3) 
				{
						document.getElementById('form_submit').style.display='none';
						document.getElementById('form_sending').style.display='block';
						document.getElementById('error_msg').style.display='none';
						return false;
				}
		 	}
			xhttp.open("GET", "../custom-code/functions.php?method=new_register&wp_email="+wp_email+"&fn="+fn+"&ln="+ln+"&loc="+loc+"&aff="+aff+"&email1="+email1+"&email2="+email2+"&website="+website+"&pass1="+pass1+"&pass2="+pass2+"&script_coverage="+script_coverage, true);
			xhttp.send();
	}
	else
	{
		alert('Must agree terms and conditions to countiue');
	}
	return false;
}


function save_guest()
{
	
	var fn=document.getElementById('fname').value;
	var ln=document.getElementById('lname').value;
	var loc=document.getElementById('location').value;
	var aff=document.getElementById('affiliation').value;
	var email1=document.getElementById('email').value;
	var email2=document.getElementById('reemail').value;
	var yt_url=document.getElementById('yt_url').value;
	var scene=document.getElementById('scene').value;
	
	{
			var xhttp = new XMLHttpRequest();
			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xhttp = new XMLHttpRequest();
			} else {
				// code for IE6, IE5
				xhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xhttp.onreadystatechange = function() 
			{
				if (xhttp.readyState == 4 && xhttp.status == 200) 
				{
					var response= xhttp.responseText;
					if(response=='success')
					{
					}
					if(response=='emailfailed')
					{
						document.getElementById('reg_form').style.display='none';
						document.getElementById('success_msg').innerHTML='Form has been submitted. Email sending failed';
						document.getElementById('error_msg').style.display='none';
						return false;
					}
					else
					{
						document.getElementById('error_msg').style.display='block';
						document.getElementById('error_msg').innerHTML=xhttp.responseText;
						document.getElementById('form_submit').style.display='block';
						document.getElementById('form_sending').style.display='none';
						scroll('error_msg');
						return false;
					}
				}
				if(xhttp.readyState == 3) 
				{
						document.getElementById('form_submit').style.display='none';
						document.getElementById('form_sending').style.display='block';
						document.getElementById('error_msg').style.display='none';
						return false;
				}
		 	}
			xhttp.open("GET", "../custom-code/functions.php?method=new_register&user_type=Guest&fn="+fn+"&ln="+ln+"&loc="+loc+"&aff="+aff+"&email1="+email1+"&email2="+email2+"&scene="+scene+"&yt_url="+yt_url, true);
			xhttp.send();
	}
	return false;
}

function update()
{
	var fn=document.getElementById('fname').value;
	var ln=document.getElementById('lname').value;
	var loc=document.getElementById('location').value;
	var aff=document.getElementById('affiliation').value;
	var email1=document.getElementById('email').value;
	var email2=document.getElementById('reemail').value;
	var website=document.getElementById('website').value;
	var current_pass1=document.getElementById('current_pass1').value;
	var wp_email=document.getElementById('wp_email').value;
	var script_coverage=document.getElementById('script_coverage').value;
	
			var xhttp = new XMLHttpRequest();
			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xhttp = new XMLHttpRequest();
			} else {
				// code for IE6, IE5
				xhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xhttp.onreadystatechange = function() 
			{
				if (xhttp.readyState == 4 && xhttp.status == 200) 
				{
					var response= xhttp.responseText;
					if(response=='success')
					{
						alert('Profile Updated');
						location.reload();
						return false;
					}
					else
					{
						document.getElementById('error_msg').style.display='block';
						document.getElementById('error_msg').innerHTML=xhttp.responseText;
						document.getElementById('form_submit').style.display='block';
						document.getElementById('form_sending').style.display='none';
						scroll('error_msg');
						return false;
					}
				}
				if(xhttp.readyState == 3) 
				{
						document.getElementById('form_submit').style.display='none';
						document.getElementById('form_sending').style.display='block';
						document.getElementById('error_msg').style.display='none';
						return false;
				}
		 	}
			xhttp.open("GET", "../custom-code/functions.php?method=update&wp_email="+wp_email+"&fn="+fn+"&ln="+ln+"&loc="+loc+"&aff="+aff+"&email1="+email1+"&email2="+email2+"&website="+website+"&current_pass1="+current_pass1+"&script_coverage="+script_coverage, true);
			xhttp.send();
			
	
	return false;
}



function change_password()
{
	var current_pass=document.getElementById('change_current_pass').value;
	var new_pass1=document.getElementById('new_pass1').value;
	var new_pass2=document.getElementById('new_pass2').value;
	var wp_email=document.getElementById('wp_email').value;
	
			var xhttp = new XMLHttpRequest();
			if (window.XMLHttpRequest) {
				// code for IE7+, Firefox, Chrome, Opera, Safari
				xhttp = new XMLHttpRequest();
			} else {
				// code for IE6, IE5
				xhttp = new ActiveXObject("Microsoft.XMLHTTP");
			}
			xhttp.onreadystatechange = function() 
			{
				if (xhttp.readyState == 4 && xhttp.status == 200) 
				{
					var response= xhttp.responseText;
					if(response=='success')
					{
						alert('Password Changed');
						location.reload();
						return false;
					}
					else
					{
						document.getElementById('error_msg_change_pass').style.display='block';
						document.getElementById('error_msg_change_pass').innerHTML=xhttp.responseText;
						document.getElementById('form_change_password').style.display='block';
						document.getElementById('form_sending_change_password').style.display='none';
						scroll('error_msg');
						return false;
					}
				}
				if(xhttp.readyState == 3) 
				{
						document.getElementById('form_change_password').style.display='none';
						document.getElementById('form_sending_change_password').style.display='block';
						document.getElementById('error_msg_change_pass').style.display='none';
						return false;
				}
		 	}
			xhttp.open("GET", "../custom-code/functions.php?method=change_password&wp_email="+wp_email+"&current_pass="+current_pass+"&new_pass1="+new_pass1+"&new_pass2="+new_pass2, true);
			xhttp.send();
			
	
	return false;
}

function scroll(element){   
var ele = document.getElementById(element);   
window.scrollTo(ele.offsetLeft,ele.offsetTop);
}

     