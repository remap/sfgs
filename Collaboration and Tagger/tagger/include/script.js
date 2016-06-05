/** JS**/
function load_playlist(method)
{
	var search_kw='';
	if(method=="search")
		search_kw=document.getElementById("search_box").value;
		
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
					if(response=='error')
					{
						alert('Error in loading playlist');
						return false;
					}
					else
					{
						document.getElementById('playlist').innerHTML=response;
						if(method=='load')
						{
							load_channel_meta();
							document.getElementById('channel_meta').style.display='block';
							document.getElementById('search_panel').style.display='block';
						}
						document.getElementById('playlist').style.display='block';
						document.getElementById('loading_icon').style.display='none';
						return false;
					}
				}
				else 
				{
						//document.getElementById('form_submit').style.display='none';
						document.getElementById('loading_icon').style.display='block';
						document.getElementById('playlist').style.display='none';
						
						if(method=='load')
						{
							document.getElementById('channel_meta').style.display='none';
						}
						//document.getElementById('error_msg').style.display='none';
						return false;
				}
		 	}
			xhttp.open("GET", "include/code.php?method=load_playlist&kw="+search_kw, true);
			xhttp.send();
}


function load_channel_meta()
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
					document.getElementById('channel_meta').innerHTML=response;
				}
		 	}
			xhttp.open("GET", "include/code.php?method=load_channel_meta", true);
			xhttp.send();
}


function update_tags(video)
{
	var tag1=document.getElementById(video+"_txt1").value;
	var tag2=document.getElementById(video+"_txt2").value;
	var tag3=document.getElementById(video+"_txt3").value;
	var tag4=document.getElementById(video+"_txt4").value;
	var tag5='';
	var tag6='';
	var tag7='';
	
	if(document.getElementById(video+"_chk1").checked == true)
		tag5=document.getElementById(video+"_chk1").value;
	if(document.getElementById(video+"_chk2").checked == true)
		tag6=document.getElementById(video+"_chk2").value;
	if(document.getElementById(video+"_chk3").checked == true)
		tag7=document.getElementById(video+"_chk3").value;
	
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
					if(response=='updated')
					{
						document.getElementById(video+'_msg').innerHTML='Tags Updated';
					}
					else
					{
						document.getElementById(video+'_msg').innerHTML=response;
					}
				}
		 	}
			xhttp.open("GET", "include/code.php?method=update_tags&video_id="+video+"&tag1="+tag1+"&tag2="+tag2+"&tag3="+tag3+"&tag4="+tag4+"&tag5="+tag5+"&tag6="+tag6+"&tag7="+tag7, true);
			xhttp.send();
}