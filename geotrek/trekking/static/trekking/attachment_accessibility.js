(function () {
    //
    // Update attachment
    //
    $('.update-accessibility-action').click(function (e) {
        e.preventDefault();

        var $this = $(this);
        var updateUrl = $this.data('update-url');
        console.log(updateUrl);
        var $form = $('.file-attachment-accessibility-form');
        var spinner = new Spinner({length: 3, radius: 5, width: 2}).spin($form[0]);
        $.get(updateUrl, function (html) {
            $form.find('.create').remove();
            $form.find('.update').html(html);
            spinner.stop();
            // Update title on file change
            watchFileInput();
            // On cancel, restore Create form
            $('#button-id-cancel').click(function () {
                $form.find('.update').html('');
                $form.find('.create').show();
            });
        });

        return false;
    });


    //
    // Delete single attachment with confirm modal
    //
    $('.delete-accessibility-action').click(function (e) {
        e.preventDefault();

        var $this = $(this);
        var deleteUrl = $this.data('delete-url');
        var $modal = $('.confirm-modal-accessibility');
        var $attachment = $this.parents('tr');

        $modal.confirmModal({
            heading: $modal.data('confirm-delete-heading'),
            body: $modal.data('confirm-delete-msg').replace('{file}', $attachment.data('title')),
            closeBtnText: $modal.data('confirm-delete-close-button'),
            confirmBtnText: $modal.data('confirm-delete-confirm-button'),
            callback: function() {
                window.location = deleteUrl;
            }
        });

        return false;
    });

    //
    // Attachment form
    //
    function watchFileInput () {
        var $form = $('form.attachments-accessibility');
        console.log($form);
        var $file_input = $form.find('input[type="file"]');

        $file_input.on('change', function (e) {
            var chosenFiles = e.currentTarget.files;
            if (chosenFiles.length === 0)
                return;
            var filename = chosenFiles[0].name;
            // Remove extension from filename
            filename = filename.replace(/\.[^/.]+$/, "");
            $form.find('input[name="title"]').val(filename);
        });
    }

    watchFileInput();
})();