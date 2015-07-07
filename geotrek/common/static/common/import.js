function updateImportProgressBars() {
	$.get('/import-update', function(datas) {
			if(datas) {
    			document.getElementById('progress-bars').innerHTML = datas;
    		}
		}
	);
}

$(document).ready(function() {
    setInterval(updateImportProgressBars, 2000);
});
