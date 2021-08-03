MapEntity.History = L.Class.extend({

    saveListInfo: function (infos) {
        $('#nbresults').text(infos.nb);
        localStorage.setItem('list-search-results', JSON.stringify(infos));
    },

    remove: function (path) {
        $.post(window.SETTINGS.urls.root + 'history/delete/', {path: path}, function() {
            var entries = $("#historylist > li")
              , entry = $("#historylist li a[href='" + path + "']").parents('li')
              , closeCurrent = String(window.location).indexOf(path, window.location.length - path.length) !== -1;
            if (closeCurrent) {
                // Closing current...
                if (entries.length > 2) {
                    // More left
                    entries.find(' > a').get(1).click();
                    $(entry).remove();
                }
                else {
                    // No more, redirect to list view
                    window.location = window.SETTINGS.urls.root;
                    $(entry).remove();
                }
            }
            else {
                $(entry).remove();
            }
        });
    },

    render: function () {
        var history = this;

        // Show number of results
        infos = localStorage.getItem('list-search-results') || '{"nb": "?", "model": null}';
        infos = JSON.parse(infos);
        $('#nbresults').text(infos.nb);
        $('#entitylist-dropdown').parent('li').addClass(infos.model);

        $('#historylist a').tooltip({'placement': 'bottom'});
        $('#historylist button.close').click(function (e) {
            e.preventDefault();
            var path = $(this).parents('a').attr('href');
            history.remove(path);
        });

        $('#historylist a').hoverIntent(
            function (e) {
                $(this).find('.close').removeClass('d-none');
                $(this).data('original-text', $(this).find('.content').text());
                var title = $(this).data('original-title');
                if (title)
                    $(this).find('.content').text(title);
            },
            function (e) {
                $(this).find('.content').text($(this).data('original-text'));
                $(this).find('.close').addClass('d-none');
            }
        );
    },
});

MapEntity.history = new MapEntity.History();