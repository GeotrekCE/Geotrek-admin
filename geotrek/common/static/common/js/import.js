function updateImportProgressBars() {
	$.getJSON('/commands/import-update.json', function(json) {
		parent = document.querySelector('#progress-bars');
		json.forEach(function(row) {
			var local_percent = row.result.current;
			var status_class = '';

			if (row.status === 'SUCCESS') {
				local_percent = "100";
				status_class = "bg-success";
			} else if (row.status === 'FAILURE') {
				local_percent = "100";
				status_class = "bg-danger";
			}

			// Update element if exists
			if (element = document.getElementById(row.id)) {
				element.querySelector('.progress-bar').setAttribute('style', 'width: ' + local_percent + '% ;');
				element.querySelector('.progress-bar').setAttribute('aria-valuenow', local_percent);
				element.querySelector('.progress-bar').innerHTML = local_percent + "%";

				if(!element.querySelector('.alert').classList.contains('alert-success')) {					
					// Add report if success.
					if (row.result.report) {
                        alert = element.querySelector('.alert');
						alert.classList.add('alert-success');
						message = element.querySelector('.message');
						message.innerHTML = row.result.report;
						alert.style.display = 'block';
					}
				}

			} else { //Create element in dom.
				element = document.createElement('div');
				element.innerHTML = document.querySelector('#import-template').innerHTML;
				element.id = row.id;
				element.querySelector('.progress-bar').setAttribute('style', 'width: ' + local_percent + '% ;');
				element.querySelector('.progress-bar').setAttribute('aria-valuenow', local_percent);
				element.querySelector('.progress-bar').innerHTML = local_percent + "%";

				element.querySelector('.parser').innerHTML = row.result.parser;
                element.querySelector('.filename').innerHTML = row.result.filename;

				parent.appendChild(element);
			}

			// Handle errors if any.
			if (row.result.exc_message) {
				element.querySelector('.alert').classList.add('alert-danger');
				element.querySelector('.message span').innerHTML = row.result.exc_type + " : " + row.result.exc_message;
				element.querySelector('.alert').style.display = 'block';
			}

			// Add class on status change.
			if (!element.querySelector('.progress-bar').classList.contains(status_class)) {
				element.querySelector('.progress-bar').classList.add(status_class);
			}
		});
});
}

$(document).ready(function() {
	updateImportProgressBars();
	setInterval(updateImportProgressBars, 1000);
});