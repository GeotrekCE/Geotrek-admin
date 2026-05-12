/*
* This script handles *sugar* effects on fieldsets related to the type of target. This is to clarify
* the Menu Item change form:
*
* - the `page` and `link` fieldsets visibility depends on the value of the field `target_type`,
* - `page` and `link_url` (for the default language) are displayed as required,
* - on form submit unused values are erased (for instance link URLs erased if target is a page).
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

function getFirstElementByClassName(className) {
    let elements = document.getElementsByClassName(className);
    return elements[0]
}

function addRequiredStyle() {
    let pageFieldset = getFirstElementByClassName("page_fieldset");
    pageFieldset.querySelector("label").classList.add("required");
    let linkFieldset = getFirstElementByClassName("link_fieldset");
    // `querySelector` returns the first matching element which is the label for the default translation language
    linkFieldset.querySelector("label").classList.add("required");
}

function updateFieldsetsVisibility() {
    let targetType = document.getElementById("id_target_type").value;
    let pageFieldset = getFirstElementByClassName("page_fieldset");
    let linkFieldset = getFirstElementByClassName("link_fieldset");
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

    let uncheckOpenInNewTab = function() {
        let checkbox = document.querySelector("input[name=open_in_new_tab]");
        checkbox.checked = false;
    }

    let erasePageField = function() {
        let page_select = document.querySelector("select[name=\"page\"]");
        page_select.value = undefined;
    };

    let targetType = document.getElementById("id_target_type").value;
    if (targetType === "page") {
        eraseLinkUrlFields();
        uncheckOpenInNewTab();
    } else if (targetType === "link") {
        erasePageField();
    } else {
        eraseLinkUrlFields();
        erasePageField();
        uncheckOpenInNewTab();
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
