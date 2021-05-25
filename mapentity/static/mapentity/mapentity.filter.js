MapEntity.TogglableFilter = L.Class.extend({
    includes: L.Mixin.Events,
    options: {},

    initialize: function () {
        var self = this;

        this.$button = $('#filters-btn');

        this.fields = {};
        this.visible = false;
        this.popover = $('#filters-popover')
                          .popover({
                              placement: 'right',
                              html: true,
                              content: '',
                              title: 'Useless'
                          });
        this.hover = $('#filters-hover')
                          .popover({
                              placement: 'bottom',
                              html: true,
                              content: this.infos.bind(this),
                              title: tr("Current criteria")
                          });

        this.$button.mouseenter(this.showinfo.bind(this));
        this.$button.mouseleave(this.hideinfo.bind(this));

        $('#mainfilter').find('select,input').change(function (e) {
            self.setfield(this);
        });

        // Use chosen for multiple values
        $("form#mainfilter").bind("reset", function() {
            setTimeout(function() {
                $('form#mainfilter select[multiple]').trigger('chosen:updated');
            }, 1);
        });

        // Make sure filter-set class is added if a choice is selected.
        $('#mainfilter select[multiple]').chosen().on('change', function (e) {
            var $target = $(e.target),
                name = $target.attr('name'),
                $container = $('div#id_' + name + '_chzn > ul');
            if ($(e.target).find('option:selected').length > 0) {
                $container.addClass('filter-set');
            }
            else {
                $container.removeClass('filter-set');
            }
        });


        //
        // Filters open/close
        //

        // Close button
        var toggle_func = this.toggle.bind(this);
        $('#filters-close').click(toggle_func);


        this.$button.click(function (e) {
            e.stopPropagation();

            // Open/Close from button
            self.toggle();

            // Close when click outside
            if (self.visible) {
                $(document).on('click.outside', function close_panel(e) {
                    if (self.tip().has(e.target).length === 0 &&
                        self.$button.has(e.target).length === 0) {
                        self.toggle();
                    }
                });

                self.popover.on('hidden.bs.popover', function () {
                    $(document).off('click.outside');
                });
            }
        });
    },

    tip: function () {
        return $(this.popover.data('bs.popover').tip);
    },

    showinfo: function () {
        // If popover is already visible, do not show hover
        if (this.visible)
            return;
        this.hover.popover('show');
    },

    hideinfo: function () {
        this.hover.popover('hide');
    },

    infos: function () {
        if (Object.keys(this.fields).length === 0)
            return "<p>" + tr("No filter") + "</p>";
        // We do not use handlebars just for this. If more to come, we will !
        var p = '<p><span class="filter-info">%name%</span>: %value%</p>';
        var i = '';
        for (var k in this.fields) {
            var f = this.fields[k];
            var value = f.value;
            value = value.replace(/&/g, '&amp;');
            value = value.replace(/</g, '&lt;');
            value = value.replace(/>/g, '&gt;');
            value = value.replace(/">"/g, '&quot;');
            value = value.replace(/'>'/g, '&#x27;');
            i += p.replace('%name%', f.label).replace('%value%', value);
        }
        return i;
    },

    toggle: function () {
        /* Show/Hide popover */
        if (this.visible) {
            // The whole $tip will be deleted, save the panel
            // and add it to the DOM so the dynamic filters still works.
            $('#filters-wrapper').append(
                this.tip().find('#filters-panel').detach()
            );
        }

        this.popover.popover('toggle');
        this.visible = !this.visible;

        if (this.visible) {
            this.hideinfo();
            this.tip()
              .empty()
              .append('<div class="arrow"/>')
              .append($('#filters-wrapper #filters-panel').detach());

            // Adjust popover width
            this.tip()
                .width(this.tip().find('#filters-panel form').outerWidth());
        }
    },

    setfield: function (field) {
        var label = $(field).data('label'),
            name = $(field).attr('name'),
            val = $(field).val(),
            set = val !== '' && val != [''];

        // Consider a value set if it is not the first option selected
        if ($(field).is('input[type=hidden]')) {
            set = false;
        }
        else if ($(field).is('select[multiple]')) {
            set = val !== null;
        }
        else if ($(field).is('select')) {
            set = val != $(field).find('option').first().val();
        }

        // Displayed value
        var value = val;
        if (field.tagName == 'SELECT') {
            value = $(field).find("option:selected").toArray().map(function (node) {
                return $(node).text()
            }).join(', ')
        }
        if (set) {
            this.fields[name] = {name: name, val:val, value:value, label:label};
        }
        else {
            delete this.fields[name];
        }

        if (set) {
            $(field).addClass('filter-set');
        }
        else {
            $(field).removeClass('filter-set');
        }
        return set;
    },

    setsubmit: function () {
        this.submitted = true;
        // Show fields as bold
        // Show button as active
        if (Object.keys(this.fields).length === 0) {
            $('#filters-btn').addClass('btn-info');
            $('#filters-btn').removeClass('btn-warning');
        }
        else {
            $('#filters-btn').removeClass('btn-info');
            $('#filters-btn').addClass('btn-warning');
        }
    }
});
