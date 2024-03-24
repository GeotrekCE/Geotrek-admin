/*
* This script handles *sugar* effects on fieldsets related to the type of target on the Menu Item change form:
* - `page` and `link_url` (for the default language) are displayed as required,
* - the `page` and `link` fieldsets visibility depends on the value of the field `target_type`,
* - on form submit erase not needed values regarding the type of target (for instance link URLs erased if target is a page).
*
* Note that `page` and `link_url` are not required regarding the <input> elements, the validation takes place on the
* server side.
*
* */

function show(element) {
    element.classList.remove("hidden");
}

function hide(element) {
    element.classList.add("hidden");
}

function addRequiredStyle() {
    let pageFieldset = document.getElementsByClassName("page_fieldset")[0];
    pageFieldset.querySelector("label").classList.add("required");
    let linkFieldset = document.getElementsByClassName("link_fieldset")[0];
    // `querySelector` returns the first matching element which is the label for the default translation language
    linkFieldset.querySelector("label").classList.add("required");
}

function updateFieldsetsVisibility() {
    let targetType = document.getElementById("id_target_type").value;
    let pageFieldset = document.getElementsByClassName("page_fieldset")[0];
    let linkFieldset = document.getElementsByClassName("link_fieldset")[0];
    if (targetType === "page") {
        show(pageFieldset);
        hide(linkFieldset);
    } else if (targetType === "link") {
        hide(pageFieldset);
        show(linkFieldset);
    } else {
        hide(pageFieldset);
        hide(linkFieldset);
    }
}

function cleanSubmission() {

    let eraseLinkUrlFields = function() {
        let inputs = document.querySelectorAll("input");
        inputs.forEach((elmt) => {
            if (elmt.name.startsWith("link_url")) {
                elmt.value = "";
            }
        });
    };

    let erasePageField = function() {
        let page_select = document.querySelector("select[name=\"page\"]");
        page_select.value = undefined;
    };

    let targetType = document.getElementById("id_target_type").value;
    if (targetType === "page") {
        eraseLinkUrlFields();
    } else if (targetType === "link") {
        erasePageField();
    } else {
        eraseLinkUrlFields();
        erasePageField();
    }
}

document.addEventListener("DOMContentLoaded", function(event) {
    addRequiredStyle();
    updateFieldsetsVisibility();

    let targetTypeSelector = document.getElementById("id_target_type");
    targetTypeSelector.addEventListener("change", updateFieldsetsVisibility);

    let form = document.getElementById("menuitem_form");
    jQuery(form).submit(cleanSubmission);
});
