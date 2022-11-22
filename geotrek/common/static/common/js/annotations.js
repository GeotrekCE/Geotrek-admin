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
if (query.lastannotation && query.clickmode !== 'brush') {
    $('.annotationtype button').removeClass('lastused');
    $('.annotationtype button#' + query.lastannotation).addClass('lastused');
}

function initAnnotations(map) {

    var annotationDebug = {};

    var layer, fromButtonSelect, fromGeojsonUpdate;

    var initialGeoJSON = query.geojson;

    $('#controls').on('change', change_controls);
    $('#geojson[type=textarea]').on('input propertychange', change_geojson);
    $('#controls').on('click', 'a', select_control);
    $('.annotationtype button').on('click', select_annotation);

    $('#controls').toggleClass('no-controls', query.controls === 'false');

    layer = map.createLayer('annotation', {
        renderer: query.renderer ? (query.renderer === 'html' ? null : query.renderer) : undefined,
        annotations: query.renderer ? undefined : geo.listAnnotations(),
        showLabels: query.labels !== 'false',
        clickToEdit: !query.clickmode || query.clickmode === 'edit'
    });


    layer.geoOn(geo.event.mouseclick, mouseClickToStart);
    layer.geoOn(geo.event.annotation.mode, handleModeChange);
    layer.geoOn(geo.event.annotation.add, handleAnnotationChange);
    layer.geoOn(geo.event.annotation.update, handleAnnotationChange);
    layer.geoOn(geo.event.annotation.remove, handleAnnotationChange);
    layer.geoOn(geo.event.annotation.state, handleAnnotationChange);

    let brushLayer;

    map.draw();

    if (query.lastused || query.active) {
        if (query.active && query.clickmode !== 'brush') {
            layer.mode(query.active);
        } else {
            $('.annotationtype button').removeClass('lastused active');
            $('.annotationtype button#' + (query.lastused || query.active)).addClass('lastused');
        }
    }

    if (initialGeoJSON) {
        layer.geojson(initialGeoJSON, true);
    }

    // if (query.clickmode === 'brush') {
    //     setBrushMode();
    // }

    annotationDebug.map = map;
    annotationDebug.layer = layer;
    annotationDebug.query = query;

    /**
     * When the mouse is clicked, switch to adding an annotation if appropriate.
     *
     * @param {geo.event} evt geojs event.
     */
    function mouseClickToStart(evt) {
        if (evt.handled || query.clickmode !== 'add') {
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
     * Handle a click or drag with a brush.
     *
     * @param {object} evt The event with the activity.
     * */
    let lastState;
    function brushAction(evt) {
        let source;
        if (evt.event === geo.event.annotation.cursor_action) {
            if (evt.operation && evt.operation !== 'union' && evt.operation !== 'difference') {
                return;
            }


            if (lastState && lastState.stateId && lastState.stateId === evt.evt.state.stateId) {
                const size = parseInt($('#brushsize').val());
                source = brushLayer.toPolygonList();
                const bbox1 = brushLayer.annotations()[0]._coordinates();
                const bbox2 = lastState.bbox;
                if (bbox1[0].x !== bbox2[0].x || bbox1[0].y !== bbox2[0].y) {
                    const order = (bbox1[0].x - bbox2[0].x) * (bbox1[0].y - bbox2[0].y) < 0 ? 0 : 1;
                    source.push([[
                        [bbox1[order].x, bbox1[order].y],
                        [bbox1[order + 2].x, bbox1[order + 2].y],
                        [bbox2[order + 2].x, bbox2[order + 2].y],
                        [bbox2[order].x, bbox2[order].y]
                    ]]);
                }
            }
            lastState = evt.evt.state;
            lastState.bbox = brushLayer.annotations()[0]._coordinates();
        } else {
            lastState = null;
        }
        geo.util.polyops[evt.operation || 'union'](layer, source || brushLayer, { correspond: {}, keepAnnotations: 'exact', style: layer });
    }

    /**
     * If the brush mode ends but we are supposed to be in brush mode, reset it.
     */
    var inUpdateBrushMode;
    function updateBrushMode() {
        if (query.clickmode !== 'brush') {
            return;
        }
        if (!inUpdateBrushMode) {
            inUpdateBrushMode = true;
            window.setTimeout(() => {
                setBrushMode();
                inUpdateBrushMode = false;
            }, 1);
        }
    }

    /**
     * If we are switching to brush mode, create an annotation that will be used
     * and hook to annotation cursor events.  If switching away, remove such an
     * annotation.
     */
    function setBrushMode(mode) {
        if (brushLayer) {
            brushLayer.mode(null);
            brushLayer.removeAllAnnotations();
        }
        if (query.clickmode !== 'brush') {
            return;
        }
        layer.mode(null);
        if (!brushLayer) {
            brushLayer = map.createLayer('annotation', {
                renderer: query.renderer ? (query.renderer === 'html' ? null : query.renderer) : undefined,
                showLabels: false
            });
            brushLayer.geoOn(geo.event.annotation.cursor_click, brushAction);
            brushLayer.geoOn(geo.event.annotation.cursor_action, brushAction);
            brushLayer.geoOn(geo.event.annotation.mode, updateBrushMode);
            brushLayer.geoOn(geo.event.annotation.state, updateBrushMode);
        }
        annotationDebug.brushLayer = brushLayer;
        const size = parseInt($('#brushsize').val());
        console.log(size);
        const annot = geo.registries.annotations['square'].func({ layer: layer });
        brushLayer.addAnnotation(annot);
        annot._coordinates([{ x: 0, y: 0 }, { x: size, y: 0 }, { x: size, y: size }, { y: size, x: 0 }]);
        brushLayer.mode(brushLayer.modes.cursor, annot);
        map.draw();
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
        switch (param) {
            case 'labels':
                layer.options('showLabels', '' + value !== 'false');
                layer.draw();
                break;
            case 'clickmode':
                layer.options('clickToEdit', value === 'edit');
                layer.draw();
                if (value === 'brush') {
                    $('.annotationtype button').removeClass('lastused active');
                    query.lastused = query.active ? query.active : query.lastused;
                    query.active = undefined;
                }
                break;
        }
        query[param] = value;
        if (value === '' || (ctl.attr('placeholder') &&
            value === ctl.attr('placeholder'))) {
            delete query[param];
        }

        setQuery(query);
        if (['clickmode'].indexOf(param) >= 0) {
            setBrushMode();
        }
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
        if (query.clickmode === 'brush') {
            query.clickmode = 'edit';
            layer.options('clickToEdit', true);
            $('#clickmode').val(query.clickmode);
            setQuery(query);
            setBrushMode();
        }
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

        if (!mode && !fromButtonSelect && query.clickmode !== 'brush') {
            layer.mode($('.annotationtype button.lastused').attr('id'));
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
            entry.find('.entry-name').text(annotation.name());
            $('#annotationlist').append(entry);
        });
        $('#annotationheader').css(
            'display', $('#annotationlist .entry').length <= 1 ? 'none' : 'block');
        if (!fromGeojsonUpdate) {


            var geojson = layer.geojson();
            $('#geojson').val(geojson ? JSON.stringify(geojson, undefined, 2) : '');
            if (query.save) {
                query.geojson = geojson ? JSON.stringify(geojson) : undefined;
                setQuery(query);
            }
        }
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
            id = ctl.closest('.entry').attr('annotation-id'),
            annotation = layer.annotationById(id);
        switch (action) {
            case 'adjust':
                layer.mode(layer.modes.edit, annotation);
                layer.draw();
                break;
            case 'edit':
                show_edit_dialog(id);
                break;
            case 'remove':
                layer.removeAnnotation(annotation);
                break;
            case 'remove-all':
                fromButtonSelect = true;
                mode = layer.mode();
                layer.mode(null);
                layer.removeAllAnnotations();
                layer.mode(mode);
                fromButtonSelect = false;
                break;
        }
    }

    /**
     * Show the edit dialog for a particular annotation.
     *
     * @param {number} id the annotation id to edit.
     */
    function show_edit_dialog(id) {
        var annotation = layer.annotationById(id),
            type = annotation.type(),
            typeMatch = new RegExp('(^| )(' + type + '|all)( |$)'),
            opt = annotation.options(),
            dlg = $('#editdialog');

        $('#edit-validation-error', dlg).text('');
        dlg.attr('annotation-id', id);
        dlg.attr('annotation-type', type);
        $('[option="name"]', dlg).val(annotation.name());
        $('[option="label"]', dlg).val(annotation.label(undefined, true));
        $('[option="description"]', dlg).val(annotation.description());


        $('.form-group[annotation-types]').each(function () {
            var ctl = $(this),
                key = $('[option]', ctl).attr('option'),
                format = $('[option]', ctl).attr('format'),
                value;
            if (!ctl.attr('annotation-types').match(typeMatch)) {


                ctl.hide();
                return;
            }
            ctl.show();
            switch ($('[option]', ctl).attr('optiontype')) {
                case 'option':
                    value = opt[key];
                    break;
                case 'label':
                    value = (opt.labelStyle || {})[key];
                    break;
                default:
                    value = opt.style[key];
                    break;
            }
            switch (format) {
                case 'angle':
                    if (value !== undefined && value !== null && value !== '') {
                        value = '' + +(+value * 180.0 / Math.PI).toFixed(4) + ' deg';
                    }
                    break;
                case 'color':


                    value = geo.util.convertColorToHex(value || { r: 0, g: 0, b: 0 }, 'needed');
                    break;
                case 'coordinate2':
                    if (value !== undefined && value !== null && value !== '') {
                        value = '' + value.x + ', ' + value.y;
                    }
            }
            if ((value === undefined || value === '' || value === null) && $('[option]', ctl).is('select')) {
                value = $('[option] option', ctl).eq(0).val();
            }
            $('[option]', ctl).val(value === undefined ? '' : '' + value);
        });
        dlg.one('shown.bs.modal', function () {
            $('[option="name"]', dlg).focus();
        });
        dlg.modal();
    }
}
