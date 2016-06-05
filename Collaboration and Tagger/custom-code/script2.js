

var x = document.getElementsByClassName("replace");
var i;
for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
}

function saveUpdatedData(email)
{
	if(confirm('Commit Changes?')==true)
    {    return updateDatabyAdmin(email);
		replace_back(email);
	}
}


function updateDatabyAdmin(email)
{

	var fn=document.getElementById(email+'first_name'+'_input').value;
	var ln=document.getElementById(email+'last_name'+'_input').value;
	var loc=document.getElementById(email+'location'+'_input').value;
	var aff=document.getElementById(email+'aff'+'_input').value;
	var emailid=document.getElementById(email+'email'+'_input').value;
	var wp_email=document.getElementById(email+'wp_email'+'_input').value;
	var website=document.getElementById(email+'website'+'_input').value;
	var url_gplus=document.getElementById(email+'url_gplus'+'_input').value;
	var url_yt=document.getElementById(email+'url_yt'+'_input').value;
	var gdrive=document.getElementById(email+'gdrive'+'_input').value;
	var shots_count=document.getElementById(email+'shots_count'+'_input').value;
	var videos_count=document.getElementById(email+'videos_count'+'_input').value;
	var script_coverage=document.getElementById(email+'script_coverage'+'_input').value;
	var script_progress=document.getElementById(email+'script_progress'+'_input').value;
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
						alert('Changes Committed');
						var objects = ['email', 'first_name', 'last_name', 'aff', 'location', 'website', 'url_gplus', 'url_yt', 'videos_count', 'script_coverage', 'script_progress', 'shots_count'];
					   
						n=objects.length; //number of elements in objects array
						for(var i=0; i<n;i++)	
						{
							var current_object = email+objects[i];
							document.getElementById(current_object).innerHTML=document.getElementById(current_object+'_input').value;
						}
					}
					else
					{
						alert(response);
						return false;
					}
				}
		 	}
			xhttp.open("GET", "../custom-code/functions.php?method=updateByAdmin&wp_email="+wp_email+"&fn="+fn+"&ln="+ln+"&loc="+loc+"&aff="+aff+"&email="+emailid+"&url_gplus="+url_gplus+"&website="+website+"&gdrive="+gdrive+"&url_yt="+url_yt+"&script_coverage="+script_coverage+"&script_progress="+script_progress+"&videos_count="+videos_count+"&shots_count="+shots_count, true);
			xhttp.send();
			
	
	return false;
}

      
 function replace_with_input(email)
 {	
	var objects = ['email', 'first_name', 'last_name', 'aff', 'location', 'website', 'url_gplus', 'url_yt', 'gdrive', 'videos_count', 'script_coverage', 'script_progress', 'shots_count'];
   
    n=objects.length; //number of elements in objects array
	for(var i=0; i<n;i++)	
	{
		var current_object = email+objects[i];
    	document.getElementById(current_object).style.display='none';
    	document.getElementById(current_object+'_input').style.display='inline';
    	document.getElementById(current_object+'_input').value=document.getElementById(current_object).innerHTML;
	}
    	document.getElementById(email+'saveLink').style.display='inline';
    	document.getElementById(email+'editLink').style.display='none';
}
function replace_back(email)
{
	var objects = ['email', 'first_name', 'last_name', 'aff', 'location', 'website', 'url_gplus', 'url_yt', 'gdrive', 'videos_count', 'script_coverage', 'script_progress', 'shots_count'];
   
    n=objects.length; //number of elements in objects array
	for(var i=0; i<n;i++)	
	{
		var current_object = email+objects[i];
    	document.getElementById(current_object+'_input').style.display='none';
    	document.getElementById(current_object).style.display='inline';
	}
    	document.getElementById(email+'saveLink').style.display='none';
    	document.getElementById(email+'editLink').style.display='inline';
}