/*
  Note: We have included the plugin in the same JavaScript file as the TinyMCE
  instance for display purposes only. Tiny recommends not maintaining the plugin
  with the TinyMCE instance and using the `external_plugins` option.
*/

document.addEventListener("DOMContentLoaded", function () {
    tinymce.PluginManager.add('button-link', function (editor, url) {
        var openDialogButtonLink = function (defaultValues, element) {
            return editor.windowManager.open({
                title: 'Lien bouton',
                body: {
                    type: 'panel',
                    items: [
                        {
                            type: 'input',
                            name: 'label',
                            label: 'Intitulé',
                        },
                        {
                            type: 'input',
                            name: 'link',
                            label: 'Lien',
                        },
                        {
                            type: 'checkbox',
                            name: 'target',
                            label: 'Ouvrir dans un nouvel onglet'
                        }
                    ]
                },
                buttons: [
                    {
                        type: 'cancel',
                        text: 'Close'
                    },
                    {
                        type: 'submit',
                        text: 'Save',
                        primary: true
                    }
                ],
                initialData: {
                    label: defaultValues && defaultValues.label || tinymce.activeEditor.selection.getContent(),
                    target: defaultValues ? !!defaultValues.target : false,
                    link: defaultValues ? defaultValues.link.replace(window.location.origin, '') : ''
                },
                onSubmit: function (api) {
                    var data = api.getData();
                    if (!data.link || !data.label) {
                        return;
                    }
                    if (element) {
                        element.textContent = data.label;
                        element.href = data.link.replace(window.location.origin, '');
                        if (data.target) {
                            element.setAttribute('target', '_blank')
                            element.setAttribute('rel', 'noopener noreferrer')
                        } else {
                            element.removeAttribute('target')
                            element.removeAttribute('rel')
                        }
                    } else {
                        var target = data.target ? ' target="_blank" rel="noopener noreferrer" ' : '';
                        editor.insertContent('<a class="button-link"' + target + 'href="' + data.link + '">' + data.label + '</a>');
                    }
                    api.close();
                }
            });
        };

        var openDialogSuggestion = function (defaultValues, element) {
            return editor.windowManager.open({
                title: 'Suggestions',
                body: {
                    type: 'panel',
                    items: [
                        {
                            type: 'listbox',
                            name: 'type',
                            label: 'Type',
                            items: [
                                {value: 'trek', text: 'Trek'},
                                {value: 'touristicContent', text: 'Touristic content'},
                                {value: 'touristicEvent', text: 'Touristic event'},
                                {value: 'outdoorSite', text: 'Outdoor site'},
                            ]
                        },
                        {
                            type: 'input',
                            name: 'label',
                            label: "Intitulé de l'encart",
                        },
                        {
                            type: 'input',
                            name: 'ids',
                            label: "Liste d'ID (séparés par des virgules)",
                        }
                    ]
                },
                buttons: [
                    {
                        type: 'cancel',
                        text: 'Close'
                    },
                    {
                        type: 'submit',
                        text: 'Save',
                        primary: true
                    }
                ],
                initialData: Object.assign(defaultValues || {}, {
                    label: defaultValues && defaultValues.label || tinymce.activeEditor.selection.getContent(),
                }),
                onSubmit: function (api) {
                    var data = api.getData();
                    if (!data.type || !data.ids) {
                        return;
                    }
                    if (element) {
                        element.dataset.label = data.label;
                        element.dataset.type = data.type;
                        element.dataset.ids = data.ids;
                    } else {
                        editor.insertContent('<div class="suggestions" data-label="' + data.label + '" data-type="' + data.type + '" data-ids="' + data.ids + '" style="display: none" contenteditable="false"></div>');
                    }
                    api.close();
                }
            });
        };
        /* Add a button that opens a window */
        editor.ui.registry.addButton('button-link', {
            text: 'Lien bouton',
            onAction: function () {
                /* Open window */
                openDialogButtonLink();
            }
        });
        /* Add a button that opens a window */
        editor.ui.registry.addButton('suggestions', {
            text: 'Suggestions',
            onAction: function () {
                /* Open window */
                openDialogSuggestion();
            }
        });

        /* Edit button-link/suggestions block when clicking on it */
        editor.on('click', function (e) {
            const element = e.target;
            if (element.classList.contains('button-link')) {
                openDialogButtonLink({ label: element.textContent, link: element.href, target: element.target }, element)
            }
            if (element.classList.contains('suggestions')) {
                const data = element.dataset;
                openDialogSuggestion({ type: data.type, label: data.label, ids: data.ids }, element)
            }
        });
    })

}); // end of document DOMContentLoaded event handler
