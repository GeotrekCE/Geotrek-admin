(function(window, $) {
    "use strict";

    function syncHiddenOrder($select, $hiddenOrderedChildren) {
        if (!$hiddenOrderedChildren.length) {
            return;
        }

        var ids = [];
        var $tags = $select.parent().find("ul.select2-selection__rendered li[title]");

        if ($tags.length > 0) {
            $tags.each(function() {
                var tagTitle = ($(this).attr("title") || "").trim();
                if (!tagTitle) {
                    return;
                }
                var $option = $select.find("option").filter(function() {
                    return $(this).text().trim() === tagTitle;
                });
                if ($option.length) {
                    ids.push($option.val());
                }
            });
        }

        if (ids.length === 0 && $select.data("select2")) {
            var selectedData = $select.select2("data") || [];
            ids = selectedData.map(function(item) {
                return String(item.id);
            });
        }

        if (ids.length === 0) {
            ids = $select.find("option:selected").map(function() {
                return String(this.value);
            }).get();
        }

        if (ids.length > 0) {
            $hiddenOrderedChildren.val(ids.join(","));
        }
    }

    window.initOrderedChildrenSelect2 = function(selectSelector, hiddenSelector, formSelector) {
        $(document).ready(function() {
            var $select = $(selectSelector);
            var $hiddenOrderedChildren = $(hiddenSelector);
            if (!$select.length) {
                return;
            }

            $select.on("select2:select", function(evt) {
                $(evt.params.data.element).detach();
                $select.append(evt.params.data.element);
                $select.trigger("change");
                syncHiddenOrder($select, $hiddenOrderedChildren);
            });

            $select.on("select2:unselect", function() {
                syncHiddenOrder($select, $hiddenOrderedChildren);
            });

            if ($.fn.sortable) {
                $select.parent().find("ul.select2-selection__rendered").sortable({
                    containment: "parent",
                    cursor: "move",
                    update: function() {
                        setTimeout(function() {
                            syncHiddenOrder($select, $hiddenOrderedChildren);
                        }, 50);
                    }
                });
            }

            $(formSelector).on("submit", function() {
                syncHiddenOrder($select, $hiddenOrderedChildren);
            });

            setTimeout(function() {
                syncHiddenOrder($select, $hiddenOrderedChildren);
            }, 300);
        });
    };
})(window, window.jQuery);

