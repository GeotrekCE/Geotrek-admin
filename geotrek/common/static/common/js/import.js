function updateImportProgressBars() {
	$.getJSON('/commands/import-update.json', function(json) {
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

			// Update element if exists
			if (element = document.getElementById(row.id)) {
				element.querySelector('.bar').style.width = local_percent;
				element.querySelector('.pull-left').innerHTML = local_percent;

				if(!element.querySelector('.alert').classList.contains('alert-success')) {					
					// Add report if success.
					if (row.result.report) {
                        alert = element.querySelector('.alert');
						alert.classList.add('alert-success');
						alert.innerHTML = row.result.report;
						alert.style.display = 'block';
					}
				}

			} else { //Create element in dom.
				element = document.createElement('div');
				element.innerHTML = document.querySelector('#import-template').innerHTML
				element.id = row.id;
				element.querySelector('.bar').style.width = local_percent + ' : ';
				element.querySelector('.pull-left').innerHTML = local_percent;
				element.querySelector('.parser').innerHTML = row.result.parser;
                element.querySelector('.filename').innerHTML = row.result.filename;

				parent.appendChild(element);
			}

			// Handle errors if any.
			if (row.result.exc_message) {
				element.querySelector('.alert').classList.add('alert-error');
				element.querySelector('.alert span').innerHTML = row.result.exc_type + " : " + row.result.exc_message;
				element.querySelector('.alert').style.display = 'block';
			}

			// Add class on status change.
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