function updateImportProgressBars() {
	$.getJSON('/import-update.json', function(json) {
		parent = document.querySelector('#progress-bars');
		json.forEach(function(row) {
			var local_percent = row.result.current + "%";
			var status_class = 'pogress-info';

			if (row.status == 'SUCCESS') {
				local_percent = "100%";
				status_class = "progress-success";
			} else if (row.status == 'FAILURE') {
				local_percent = "100%";
				status_class = "progress-danger";
			}

			if (element = document.getElementById(row.id)) {
				element.querySelector('.bar').style.width = local_percent;
				element.querySelector('.pull-left').innerHTML = local_percent;
			} else {
				element = document.createElement('div');
				element.innerHTML = document.querySelector('#import-template').innerHTML
				element.id = row.id;
				element.querySelector('.bar').style.width = local_percent;
				element.querySelector('.pull-left').innerHTML = local_percent;

				parent.appendChild(element);
			}
			if (row.result.exc_message) {
				element.querySelector('.alert span').innerHTML = "Error message : " + row.result.exc_message;
				element.querySelector('.alert').style.display = 'block';
			}

			if (!element.querySelector('.progress').classList.contains(status_class)) {
				element.querySelector('.progress').classList.add(status_class);
			}
		});
	});
}

$(document).ready(function() {
	updateImportProgressBars();
	setInterval(updateImportProgressBars, 1000);
});