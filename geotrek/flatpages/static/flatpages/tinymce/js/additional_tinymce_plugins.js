/*
  Note: We have included the plugin in the same JavaScript file as the TinyMCE
  instance for display purposes only. Tiny recommends not maintaining the plugin
  with the TinyMCE instance and using the `external_plugins` option.
*/

document.addEventListener("DOMContentLoaded", function () {
    tinymce.PluginManager.add('button-link', function (editor, url) {
        var openDialogButtonLink = function () {
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
                    label: tinymce.activeEditor.selection.getContent(),
                },
                onSubmit: function (api) {
                    var data = api.getData();
                    if (!data.link || !data.label) {
                        return;
                    }
                    var target = data.target ? ' target="_blank" rel="noopener noreferrer" ' : '';
                    editor.insertContent('<a class="button-link"' + target + 'href="' + data.link + '">' + data.label + '</a>');
                    api.close();
                }
            });
        };

        var openDialogSuggestion = function () {
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
                initialData: {
                    label: tinymce.activeEditor.selection.getContent(),
                },
                onSubmit: function (api) {
                    var data = api.getData();
                    if (!data.type || !data.ids) {
                        return;
                    }
                    editor.insertContent('<div class="suggestions" data-label="' + data.label + '" data-type="' + data.type + '" data-ids="' + data.ids + '" style="display: none" contenteditable="false"></div>');
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
    })

}); // end of document DOMContentLoaded event handler
