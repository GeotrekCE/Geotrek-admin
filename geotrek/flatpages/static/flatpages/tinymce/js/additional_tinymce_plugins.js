/*
  Note: We have included the plugin in the same JavaScript file as the TinyMCE
  instance for display purposes only. Tiny recommends not maintaining the plugin
  with the TinyMCE instance and using the `external_plugins` option.
*/

document.addEventListener("DOMContentLoaded", function () {
    tinymce.PluginManager.add('button-link', function (editor, url) {
        var openDialogButtonLink = function (defaultValues, element) {
            return editor.windowManager.open({
                title: i18n.tinymce_Button_Link,
                body: {
                    type: 'panel',
                    items: [
                        {
                            type: 'input',
                            name: 'label',
                            label: i18n.tinymce_Label,
                        },
                        {
                            type: 'input',
                            name: 'link',
                            label: i18n.tinymce_Link,
                        },
                        {
                            type: 'checkbox',
                            name: 'target',
                            label: i18n.tinymce_Open_link_in_a_new_tab
                        }
                    ]
                },
                buttons: [
                    {
                        type: 'cancel',
                        text: i18n.tinymce_Cancel
                    },
                    {
                        type: 'submit',
                        text: i18n.tinymce_Submit,
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
                title: i18n.tinymce_Suggestions,
                body: {
                    type: 'panel',
                    items: [
                        {
                            type: 'listbox',
                            name: 'type',
                            label: 'Type',
                            items: [
                                {value: 'trek', text: i18n.tinymce_Suggestions_Trek },
                                {value: 'touristicContent', text: i18n.tinymce_Suggestions_Touristic_Content    },
                                {value: 'touristicEvent', text: i18n.tinymce_Suggestions_Touristic_Event    },
                                {value: 'outdoorSite', text: i18n.tinymce_Suggestions_Outdoor_Site  },
                            ]
                        },
                        {
                            type: 'input',
                            name: 'label',
                            label: i18n.tinymce_Suggestions_title,
                        },
                        {
                            type: 'input',
                            name: 'ids',
                            label: i18n.tinymce_Suggestions_ID_list,
                        }
                    ]
                },
                buttons: [
                    {
                        type: 'cancel',
                        text: i18n.tinymce_Cancel
                    },
                    {
                        type: 'submit',
                        text: i18n.tinymce_Submit,
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
                        // The <p> tag at the end allows the user to add content after the suggestion block
                        editor.insertContent('<div class="suggestions" data-label="' + data.label + '" data-type="' + data.type + '" data-ids="' + data.ids + '" style="display: none" contenteditable="false"></div><p></p>');
                    }
                    api.close();
                }
            });
        };

        var openDialogGalleryImages = function (defaultValues, element) {
             // Stocker les images sélectionnées
             let images = defaultValues || [];
      
             // Fonction pour mettre à jour la vue des images
             function updateImagePreview() {
               var preview = document.getElementById('image-preview');
               preview.innerHTML = '';
               images.forEach((image, index) => {
                 var imgDiv = document.createElement('li');
                 imgDiv.className = 'image-preview';
                 imgDiv.innerHTML = `
                   <span>${image.outerHTML}</span>
                   <button type="button" class="tox-button tox-button--secondary" data-index="${index}">${i18n.tinymce_Gallery_image_remove}</button>
                 `;
                 preview.appendChild(imgDiv);
               });
     
               // Ajouter des gestionnaires d'événements pour les boutons de suppression
               document.querySelectorAll('.image-preview button').forEach(button => {
                 button.addEventListener('click', function () {
                   var index = this.getAttribute('data-index');
                   images.splice(index, 1);
                   updateImagePreview();
                 });
               });
             }
     
             // Ouvrir une fenêtre modale personnalisée pour la gestion des images
             editor.windowManager.open({
               title: i18n.tinymce_Gallery_title,
               width: "80%", 
               height: "80%",
               body: {
                 type: 'panel',
                 items: [
                   {
                     type: 'htmlpanel',
                     html: '<ul id="image-preview"></ul>'
                   },
                   {
                     type: 'button',
                     text: i18n.tinymce_Gallery_image_add,
                   }
                 ]
               },
               buttons: [
                {
                    text: i18n.tinymce_Submit,
                    type: 'submit',
                    primary: true,
                },
                {
                    type: 'cancel',
                    text: i18n.tinymce_Cancel,
                    onClick: function (api) {
                        api.close();
                    }
                 }
               ],
               onAction: function () {
                    editor.selection.collapse()
                    editor.execCommand('mceImage', false);
                    editor.once('change', function () {
                        const imgElement = editor.selection.getNode();
                        if (imgElement) {
                            images.push(imgElement);
                            editor.dom.remove(imgElement);
                            updateImagePreview();
                        }
                    });
               },
               onSubmit: function (api) {
                    let galleryHtml = '<ul class="gallery-container" contenteditable="false">';
                    if (element) {
                        element.remove();
                    }
                    if (images.length === 0) {
                        api.close();
                        return;
                    }
                    images.forEach(image => {
                        galleryHtml += '<li>' + image.outerHTML + '</li>';
                    });
                    // The <p> tag at the end allows the user to add content after the gallery block
                    galleryHtml += '</ul><p><br /></p>';
                    editor.insertContent(galleryHtml);
                    api.close();
                }
             });
     
             updateImagePreview(); // Initialiser la vue des images
        };

        /* Add a button that opens a window */
        editor.ui.registry.addButton('button-link', {
            text: i18n.tinymce_Button_Link,
            onAction: function () {
                /* Open window */
                openDialogButtonLink();
            }
        });
        /* Add a button that opens a window */
        editor.ui.registry.addButton('suggestions', {
            text: i18n.tinymce_Suggestions,
            onAction: function () {
                /* Open window */
                openDialogSuggestion();
            }
        });

        editor.ui.registry.addButton('imagesGallery', {
            text: i18n.tinymce_Gallery_add,
            icon: 'image',
            onAction: function () {
                openDialogGalleryImages();
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
            if (element.classList.contains('gallery-container')) {
                const images = Array.from(element.querySelectorAll('img')) ;
                openDialogGalleryImages(images, element)
            }
        });

        /* Suppr suggestions and gallery sections properly */
        editor.on('keydown', function (event) {
            var backspaceKeyCode = 8;
            var supprKeyCode = 46;
            if (![backspaceKeyCode, supprKeyCode].includes(event.keyCode)) {
                return;
            }

            var selectedNode = editor.selection.getNode();

            var nodeToDelete = event.keyCode === backspaceKeyCode 
                ? selectedNode.previousElementSibling ?? selectedNode.parentNode.previousElementSibling
                : selectedNode.nextElementSibling ?? selectedNode.parentNode.nextElementSibling;

            var isOffsetPositionMatchToDelete = event.keyCode === backspaceKeyCode 
                ? editor.selection.getRng().startOffset === 0
                : editor.selection.getRng().startOffset === editor.selection.getRng().startContainer.length;
            
            if (
                isOffsetPositionMatchToDelete
                && nodeToDelete && nodeToDelete.classList
                && ['suggestions', 'gallery-container'].some(className => nodeToDelete.classList.contains(className))
            ) {
                event.preventDefault();
                editor.dom.remove(nodeToDelete);
            }
          }, true);
    })

}); // end of document DOMContentLoaded event handler
