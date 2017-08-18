$(document).ready(function(){
RoomConditions();



	setInterval(RoomConditions, 120000);
    function RoomConditions() {
		currentValue = $('#currentValue');
		document.getElementById("ac_temperature").innerHTML = "Loading..";
		document.getElementById("room_temperature").innerHTML = "Loading..";
		document.getElementById("room_humidity").innerHTML = "Loading..";
		 document.getElementById("outer_temperature").innerHTML = "Loading..";
		document.getElementById("slider").value = "Loading..";
		$.ajax({
				 type: 'GET',
				 url: "/getsetting",
			     contentType: "application/json; charset=utf-8",
			     dataType: "json",
				 /*crossDomain: true,
     			 xhrFields: {
	     					 withCredentials: true
							 },*/
			     success: function (data) {
				 document.getElementById("room_temperature").innerHTML = data["inner"];
				 document.getElementById("room_humidity").innerHTML = data["humidity"];
				 document.getElementById("ac_temperature").innerHTML = data["setting"];
				  document.getElementById("outer_temperature").innerHTML = data["outer"];
				 document.getElementById("slider").value = data["setting"];
				 currentValue.html(data["setting"]);
					     }
			   });
    }
								
});


