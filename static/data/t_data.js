$(function() {

		var chart1 = Morris.Line({
			element: 'morris-area-chart',
			xkey: 'date',
			ykeys: ['inner', 'outer', 'humidity'],
			labels: ['Inner Temperature', 'Outer Temperature', 'Humidity'],
			pointSize: 3,
			hideHover: 'auto',
			resize: true
			});
			
		var chart2 = Morris.Line({
			element: 'morris-area-chart1',
			xkey: 'date',
			ykeys: ['inner', 'prefered'],
			labels: ['Inner Temperature', 'user prefered Temperature'],
			pointSize: 3,
			hideHover: 'auto',
			resize: true
			});


autoRefresh_div();	
var id = setInterval(autoRefresh_div, 120000); //2 min = 120000, 15 min = 900000 mills
function autoRefresh_div() {
	
        $.ajax({
            'global': false,
            'url': '/morrisdata',
            'dataType': "json",
            'success': function (data) {
                chart1.setData(data["graph1"]);
				chart2.setData(data["graph2"]);
            },
			contentType: "application/json; charset=utf-8"
        });


    }

	
});