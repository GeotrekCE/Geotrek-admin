/* Decode query components into a dictionary of values.
   *
   * @returns {object}: the query parameters as a dictionary.
   */
function getQuery() {
    var query = document.location.search.replace(/(^\?)/, '').split(
        '&').map(function (n) {
            n = n.split('=');
            if (n[0]) {
                this[decodeURIComponent(n[0].replace(/\+/g, '%20'))] = decodeURIComponent(n[1].replace(/\+/g, '%20'));
            }
            return this;
        }.bind({}))[0];
    return query;
}

/* Encode a dictionary of parameters to the query string, setting the window
    * location and history.  This will also remove undefined values from the
    * set properites of params.
    *
    * @param {object} params: the query parameters as a dictionary.
    */
function setQuery(params) {
    $.each(params, function (key, value) {
        if (value === undefined) {
            delete params[key];
        }
    });
    var newurl = window.location.protocol + '//' + window.location.host +
        window.location.pathname + '?' + $.param(params);
    window.history.replaceState(params, '', newurl);
}

var query = getQuery();

$('#showLabels').prop('checked', query.labels !== 'false');
if (query.lastannotation) {
    $('.annotationtype button').removeClass('lastused');
    $('.annotationtype button#' + query.lastannotation).addClass('lastused');
}

function initAnnotationsWidget(map) {

    var annotationDebug = {};

    var layer, fromButtonSelect, fromGeojsonUpdate;

    var initialGeoJSON = $('#id_annotations').text();

    $('#controls').on('change', change_controls);
    $('#id_annotations[type=textarea]').on('input propertychange', change_geojson);
    $('#controls').on('click', 'a', select_control);
    $('.annotationtype button').on('click', select_annotation);

    $('#controls').toggleClass('no-controls', query.controls === 'false');

    layer = map.createLayer('annotation', {
        renderer: query.renderer ? (query.renderer === 'html' ? null : query.renderer) : undefined,
        annotations: query.renderer ? undefined : geo.listAnnotations(),
        showLabels: query.labels !== 'false',
        clickToEdit: true
    });

    layer.geoOn(geo.event.mouseclick, mouseClickToStart);
    layer.geoOn(geo.event.annotation.mode, handleModeChange);
    layer.geoOn(geo.event.annotation.add, handleAnnotationChange);
    layer.geoOn(geo.event.annotation.update, handleAnnotationChange);
    layer.geoOn(geo.event.annotation.remove, handleAnnotationChange);
    layer.geoOn(geo.event.annotation.state, handleAnnotationChange);

    map.draw();

    if (query.lastused || query.active) {
        if (query.active) {
            layer.mode(query.active);
        } else {
            $('.annotationtype button').removeClass('lastused active');
            $('.annotationtype button#' + (query.lastused || query.active)).addClass('lastused');
        }
    }

    if (initialGeoJSON) {
        layer.geojson(initialGeoJSON, true);
    }

    annotationDebug.map = map;
    annotationDebug.layer = layer;
    annotationDebug.query = query;

    /**
     * When the mouse is clicked, switch to adding an annotation if appropriate.
     *
     * @param {geo.event} evt geojs event.
     */
    function mouseClickToStart(evt) {
        if (evt.handled) {
            return;
        }
        if (evt.buttonsDown.left) {
            if ($('.annotationtype button.lastused').hasClass('active')) {
                return;
            }
            select_button('.annotationtype button.lastused');
        } else if (evt.buttonsDown.right) {
            select_button('.annotationtype button#' +
                $('.annotationtype button.lastused').attr('next'));
        }
    }

    /**
     * Handle changes to our controls.
     *
     * @param evt jquery evt that triggered this call.
     */
    function change_controls(evt) {
        var ctl = $(evt.target),
            param = ctl.attr('param-name'),
            value = ctl.val();
        if (ctl.is('[type="checkbox"]')) {
            value = ctl.is(':checked') ? 'true' : 'false';
        }
        if (value === '' && ctl.attr('placeholder')) {
            value = ctl.attr('placeholder');
        }
        if (!param || value === query[param]) {
            return;
        }
        if (param == 'labels') {
            layer.options('showLabels', '' + value !== 'false');
            layer.draw();
        }
        query[param] = value;
        if (value === '' || (ctl.attr('placeholder') &&
            value === ctl.attr('placeholder'))) {
            delete query[param];
        }
        setQuery(query);
    }

    /**
     * Handle changes to the geojson.
     *
     * @param evt jquery evt that triggered this call.
     */
    function change_geojson(evt) {
        var ctl = $(evt.target),
            value = ctl.val();


        fromGeojsonUpdate = true;
        var result = layer.geojson(value, 'update');
        if (query.save && result !== undefined) {
            var geojson = layer.geojson();
            query.geojson = geojson ? JSON.stringify(geojson) : undefined;
            setQuery(query);
        }
        fromGeojsonUpdate = false;
    }

    /**
     * Handle selecting an annotation button.
     *
     * @param evt jquery evt that triggered this call.
     */
    function select_annotation(evt) {
        select_button(evt.target);
    }

    /**
     * Select an annotation button by jquery selector.
     *
     * @param {object} ctl a jquery selector or element.
     */
    function select_button(ctl) {
        ctl = $(ctl);
        var wasactive = ctl.hasClass('active'),
            id = ctl.attr('id');
        fromButtonSelect = true;
        layer.mode(wasactive ? null : id);
        fromButtonSelect = false;
    }

    /**
     * When the annotation mode changes, update the controls to reflect it.
     *
     * @param {geo.event} evt a geojs mode change event.
     */
    function handleModeChange(evt) {
        var mode = layer.mode();
        $('.annotationtype button').removeClass('active');
        if (mode) {
            $('.annotationtype button').removeClass('lastused active');
            $('.annotationtype button#' + mode).addClass('lastused active');
        }
        $('#instructions').attr(
            'annotation', $('.annotationtype button.active').attr('id') || 'none');
        query.active = $('.annotationtype button.active').attr('id') || undefined;
        query.lastused = query.active ? undefined : $('.annotationtype button.lastused').attr('id');
        setQuery(query);

        if (!mode && !fromButtonSelect) {
            layer.mode($('.annotationtype button.lastused').attr('id'));
        }
    }

    function update_edited_label_on_enter(entry, key) {
        if (key.keyCode === 13) {
            update_edited_label(entry)
        }
    }

    /**
     * When an annotation is created or removed, update our list of annotations.
     *
     * @param {geo.event} evt a geojs mode change event.
     */
    function handleAnnotationChange(evt) {
        var annotations = layer.annotations();
        var ids = annotations.map(function (annotation) {
            return annotation.id();
        });
        var present = [];
        $('#annotationlist .entry').each(function () {
            var entry = $(this);
            if (entry.attr('id') === 'sample') {
                return;
            }
            var id = entry.attr('annotation-id');
            if ($.inArray(id, ids) < 0) {
                entry.remove();
                return;
            }
            present.push(id);
            entry.find('.entry-name').text(layer.annotationById(id).name());
        });

        $.each(ids, function (idx, id) {
            if ($.inArray(id, present) >= 0) {
                return;
            }
            var annotation = layer.annotationById(id);
            if (annotation.state() === geo.annotation.state.create) {
                return;
            }
            var entry = $('#annotationlist .entry#sample').clone();
            entry.attr({ id: '', 'annotation-id': id });
            entry.find('#label_input').val(annotation.name())
            entry.find('#label_input').on('blur', () => update_edited_label(entry));
            entry.find('#label_input').on('keydown', (key) => update_edited_label_on_enter(entry, key));

            var category_selector = $('#id_annotation_category').clone();
            category_selector.attr('for-annotation', id);
            category_selector.on("change", update_annotation_category_event)
            entry.find('.entry-validate').before(category_selector);
            entry.find('.entry-name').text(annotation.name());

            if (query.editing == id) {
                entry.find('.entry-adjust').hide();
                entry.find('.entry-validate').show();
            }
            $('#annotationlist').append(entry);
            if ($("#div_id_annotations_categories textarea").val() !== "") {
                var annotations_categories = JSON.parse($("#div_id_annotations_categories textarea").val());
                previous_category = annotations_categories[id]
                if (typeof previous_category !== 'undefined') {
                    $('#id_annotation_category[for-annotation="' + id + '"]').val(parseInt(previous_category))
                }
            }
        });
        $('#annotationheader').css(
            'display', $('#annotationlist .entry').length <= 1 ? 'none' : 'block');
        if (!fromGeojsonUpdate) {
            var geojson = layer.geojson();
            $('#id_annotations').val(geojson ? JSON.stringify(geojson, undefined, 2) : '');
            if (query.save) {
                query.geojson = geojson ? JSON.stringify(geojson) : undefined;
                setQuery(query);
            }
        }
    }

    function update_annotation_category(annotation_id, category_id) {
        if ($("#div_id_annotations_categories textarea").val() != "") {
            var annotations_categories = JSON.parse($("#div_id_annotations_categories textarea").val())
        } else {
            var annotations_categories = {}
        }
        if (category_id == "") {
            delete annotations_categories[annotation_id]
        } else {
            annotations_categories[annotation_id] = category_id
        }
        $("#div_id_annotations_categories textarea").val(JSON.stringify(annotations_categories))
    }

    function update_annotation_category_event(e) {
        category_id = e.target.value
        annotation_id = e.target.getAttribute('for-annotation')
        update_annotation_category(annotation_id, category_id)
    }

    function update_edited_label(entry) {
        // After changing annotation name in input, update it in geojson and layer
        new_label = entry.find('#label_input').val()
        // Replace name in GEOJson form
        annotation_id = entry[0].getAttribute('annotation-id');
        current_data = JSON.parse($('#id_annotations[type=textarea]').val())
        for (var i = 0; i < current_data['features'].length; ++i) {
            if (current_data['features'][i]['properties']['annotationId'] == annotation_id) {
                current_data['features'][i]['properties']['name'] = new_label;
            }
        }
        $('#id_annotations[type=textarea]').val(JSON.stringify(current_data, null, 2));
        $('#id_annotations[type=textarea]').trigger('propertychange')
        // Replace name in GEOJson layer
        var annotation = layer.annotationById(annotation_id);
        annotation.name(new_label);
    }

    /**
     * Handle selecting a control.
     *
     * @param evt jquery evt that triggered this call.
     */
    function select_control(evt) {
        var mode,
            ctl = $(evt.target),
            action = ctl.attr('action'),
            entry = ctl.closest('.entry'),
            id = entry.attr('annotation-id'),
            annotation = layer.annotationById(id);
        switch (action) {
            case 'validate':
                layer.mode(null);
                query.editing = undefined;
                setQuery(query)
                layer.draw();
                handleAnnotationChange(evt);
                break;
            case 'adjust':
                layer.mode(layer.modes.edit, annotation);
                query.editing = id;
                setQuery(query)
                layer.draw();
                handleAnnotationChange(evt);
                break;
            case 'remove':
                update_annotation_category(id, "")
                layer.removeAnnotation(annotation);
                break;
            case 'remove-all':
                fromButtonSelect = true;
                mode = layer.mode();
                layer.mode(null);
                layer.removeAllAnnotations();
                layer.mode(mode);
                $("#div_id_annotations_categories textarea").val("")
                fromButtonSelect = false;
                break;
        }
    }
}
