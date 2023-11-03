$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_site = false;
    var loaded_course = false;
    // Show outdoor layers in application maps
    $.each(['site', 'course'], function (i, modelname) {
        var style = L.Util.extend({ clickable: false },
            window.SETTINGS.map.styles[modelname] || {});
        var layer = new L.ObjectsLayer(null, {
            modelname: modelname,
            style: style,
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
        // Refresh site types by practice
        $('#id_practice').change(function () {
            update_site_types_and_cotations();
        });
        $('#id_practice').trigger('change');
    }
    if (data.modelname == 'course') {
        // Important : course must inherit practice form parent site(s). Cotations and types and practice-dependent.
        // Refresh course types and course cotations by practice on site change
        $('#id_parent_sites').change(function () {
            update_course_sites();
            update_course_types();
            update_course_cotations();
        });
        // Init cotations and types properly, at form load, when editing existing courses with existing parent(s)
        // This is because Chosen plugin is tricky
        $(document).ready(function () {
            update_course_cotations()
            update_course_types();
        });
        // Init sites properly, on selector first click, when editing existing courses with existing parent(s)
        // This is because Chosen plugin is tricky
        $(document).on("click", "#id_parent_sites_chosen", function () {
            update_course_sites();
        });
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
        if (!(scale_id in category['scales'])) {
            $('#id_rating_scale_' + scale_id).val('').trigger("chosen:updated");
        }
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

function update_course_cotations() {
    // Important : course must inherit practice form parent site(s). Cotations and types and practice-dependent.
    // JSON data mapping sites to practices and cotations and types
    var sites = JSON.parse($('#site-practices-types').text());
    // Parent sites selected in form
    var parent_sites = $('#id_parent_sites').val();
    // IF there is (are) selected parent site(s)
    if (parent_sites && parent_sites.length > 0) {
        // We use the first selected site as our reference for cotations
        site = parent_sites[0]
        // Update cotations according to mapping between sites and cotations
        update_cotations(sites[site]);
    } else {
        //ELSE there is no selected parent site, then hide all cotations
        hide_all_cotations();
    }
}

function update_course_sites() {
    // Important : course must inherit practice form parent site(s). Cotations and types and practice-dependent.
    //JSON data mapping sites to practices and cotations and types
    var sites = JSON.parse($('#site-practices-types').text());
    // Parent sites selected in form
    var parent_sites = $('#id_parent_sites').val();
    // Get all possible sites in selector as list of elements
    options = $('#id_parent_sites_chosen .chosen-drop .chosen-results li')
    // IF there is at least one selected parent site
    if (parent_sites && parent_sites.length > 0) {
        // We use the first selected site as our reference for practices
        selected_site = parent_sites[0]
        selected_practice = sites[selected_site]['practice']
        // For each Site available in selector
        for (var i = 0, len = options.length; i < len; i++) {
            // Extract site's django ID to find this site's practice in JSON mapping data
            array_index = options[i].getAttribute('data-option-array-index')
            form_element = $('#id_parent_sites option').eq(array_index)
            site_id = form_element.attr('value')
            site_practice = sites[site_id]['practice']
            // If selector for this site is activated right now
            if (1 | options.eq(i).hasClass('active-result')) {
                // Disable selector for this site IF it is not selected and has a different practice, or if selected site has null practice, because no practice should match null practice (even null practice itself)
                // ELSE show and activate this selector
                is_selected = options.eq(i).hasClass('result-selected')
                if (!(is_selected) && (selected_practice != site_practice || (selected_practice == null))) {
                    form_element.prop("disabled", true)
                } else {
                    form_element.prop("disabled", false)
                }
                $('#id_parent_sites').trigger("chosen:updated");
            }
        }
    } else { // ELSE no parent site is selected
        // Then re-activate all site selectors
        for (var i = 0, len = options.length; i < len; i++) {
            array_index = options[i].getAttribute('data-option-array-index')
            form_element = $('#id_parent_sites option').eq(array_index)
            form_element.prop("disabled", false)
            $('#id_parent_sites').trigger("chosen:updated");
        }
    }
}

function update_course_types() {
    // Important : course must inherit practice form parent site(s). Cotations and types and practice-dependent.
    //JSON data mapping sites to practices and cotations and types
    var sites = JSON.parse($('#site-practices-types').text());
    // Parent sites selected in form
    var parent_sites = $('#id_parent_sites').val();
    // Init types with empty
    var types = {}
    // IF there is at least one selected parent site
    if (parent_sites && parent_sites.length > 0) {
        // We use the first selected site as our reference for practices and their types
        selected_site = parent_sites[0]
        selected_practice = sites[selected_site]['practice']
        types = sites[selected_site]['types']
        // Refresh type selector accordingly
        var $select = $('#id_type');
        var selected = $select.val() || [];
        refresh_selector_with_types($select, types, selected);
    }
    // Hide type field if there exists no type for this site's practice
    $('#div_id_type').toggle(Object.keys(types).length > 0);
}
