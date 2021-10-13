$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_site = false;
    var loaded_course = false;
    // Show outdoor layers in application maps
    $.each(['site', 'course'], function (i, modelname) {
        var layer = new L.ObjectsLayer(null, {
            modelname: modelname,
            style: L.Util.extend(window.SETTINGS.map.styles[modelname] || {}, { clickable: false }),
        });
        if (data.modelname != modelname) {
            map.layerscontrol.addOverlay(layer, tr(modelname), tr('Outdoor'));
        };
        map.on('layeradd', function (e) {
            var options = e.layer.options || { 'modelname': 'None' };
            if (!loaded_site) {
                if (options.modelname == 'site' && options.modelname != data.modelname) {
                    e.layer.load(window.SETTINGS.urls.site_layer);
                    loaded_site = true;
                }
            }
            if (!loaded_course) {
                if (options.modelname == 'course' && options.modelname != data.modelname) {
                    e.layer.load(window.SETTINGS.urls.course_layer);
                    loaded_course = true;
                }
            }
        });
    });
});


$(window).on('entity:view:add entity:view:update', function (e, data) {
    if (data.modelname == 'site') {
        // Refresh types by practice
        $('#id_practice').change(function () {
            update_site_types_and_cotations();
        });
        $('#id_practice').trigger('change');
    }
    if (data.modelname == 'course') {
        // Refresh types by practice
        $('#id_parent_sites').change(function () {
            update_course_types_and_cotations();
        });
        $('#id_parent_sites').trigger('change');
        await new Promise(r => setTimeout(() => r(), 2000));
        update_course_types_and_cotations();
    }
    return;
});

function refresh_selector_with_types($select, types, selected) {
    $select.empty();
    $('<option/>')
        .text('---------')
        .attr('value', '')
        .appendTo($select);
    for (var type_id in types) {
        var type_name = types[type_id];
        $('<option/>')
            .text(type_name)
            .attr('value', type_id)
            .prop('selected', selected.indexOf(type_id) >= 0)
            .appendTo($select);
    }
    $select.trigger('chosen:updated');
}

function update_cotations(category) {
    // For each scale rating
    var scales = JSON.parse($('#all-ratings-scales').text());
    for (var scale_id in scales) {
        // Hide form field if scale not in list for this category
        $('#div_id_rating_scale_' + scale_id).prop('hidden', !(scale_id in category['scales']));
        $('#id_rating_scale_' + scale_id + '_chosen').width('100%');
    }
}

function hide_all_cotations() {
    // For each scale rating
    var scales = JSON.parse($('#all-ratings-scales').text());
    for (var scale_id in scales) {
        // Hide form fields
        $('#div_id_rating_scale_' + scale_id).prop('hidden', true);
    }
}

function update_site_types_and_cotations() {
    var practices = JSON.parse($('#practices-types').text());
    var practice = $('#id_practice').val();
    var $select = $('#id_type');
    var selected = $select.val() || [];

    var types = practice ? practices[practice]['types'] : {};
    // Hide type field if no values for this practice
    $('#div_id_type').toggle(Object.keys(types).length > 0);

    // Refresh options list for types, depending on practice
    refresh_selector_with_types($select, types, selected);

    // Refresh cotation selectors
    if (practice == "") {
        hide_all_cotations();
    } else {
        update_cotations(practices[practice]);
    }
}

function update_course_types_and_cotations() {
    console.log("updatin'")
    //JSON data on all sites
    var sites = JSON.parse($('#site-practices-types').text());
    // Parent sites selected in form
    var parent_sites = $('#id_parent_sites').val();
    // Init types with empty
    var types = {}
    // Get all possible sites in selector as list of elements
    options = $('#id_parent_sites_chosen .chosen-drop .chosen-results li')
    // If there is (are) selected parent site(s)
    if (parent_sites && parent_sites.length > 0) {
        // We use the first selected site as our reference for practices
        site = parent_sites[0]
        // Set types accordingly
        types = sites[site]['types']
        // Extract corresponding practice
        practice = sites[site]['practice']
        // For each Site in selectors
        for (var i = 0, len = options.length; i < len; i++) {
            // Extract index in stylish selector
            array_index = options[i].getAttribute('data-option-array-index')
            // Extract hidden form element for this stylish selector
            form_element = $('#id_parent_sites option').eq(array_index)
            // Extract site id
            site_id = form_element.attr('value')
            // If selector is enabled
            if (1 | options.eq(i).hasClass('active-result')) {
                // If selector is not selected and has a different practice than first selected site (or null practice)
                is_selected = options.eq(i).hasClass('result-selected')
                if (!(is_selected) && (practice != sites[site_id]['practice'] || (practice == null))) {
                    // Hide it away
                    form_element.prop("disabled", true)
                    $('#id_parent_sites').trigger("chosen:updated");
                } else {
                    // Else show it
                    form_element.prop("disabled", false)
                    $('#id_parent_sites').trigger("chosen:updated");
                }

            }
        }

        // Hide type field if no values for this site
        $('#div_id_type').toggle(Object.keys(types).length > 0);

        // Refresh cotation selectors
        update_cotations(sites[site]);
        // If no parent site is selected
    } else {
        //Re-activate all site selectors
        for (var i = 0, len = options.length; i < len; i++) {
            array_index = options[i].getAttribute('data-option-array-index')
            form_element = $('#id_parent_sites option').eq(array_index)
            form_element.prop("disabled", false)
            $('#id_parent_sites').trigger("chosen:updated");
        }
        // Hide cotation form fields
        hide_all_cotations();
    }

    // Finally refresh types
    var $select = $('#id_type');
    var selected = $select.val() || [];
    // Refresh options list for types, depending on site
    refresh_selector_with_types($select, types, selected);
}