$(document).ready(function () {
    $('#create_subs_form').on('submit', function (e) {
        e.preventDefault();
        $('#create_subs_button').prop('disabled', true);
        $('#vid_processing_message').show();
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                location.reload();
            }
        });
    });

    $('#translate_subs_form').on('submit', function (e) {
        e.preventDefault();
        $('#translate_subs_button').prop('disabled', true);
        $('#translation_processing_message').show();
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                location.reload();
            }
        });
    });

    $('#generate_voice_form').on('submit', function (e) {
        e.preventDefault();
        $('#generate_voice_button').prop('disabled', true);
        $('#voice_gen_processing_message').show();
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: $(this).serialize(),
            success: function (response) {
                location.reload();
            }
        });
    });


    $('form[enctype="multipart/form-data"]').on('submit', function (e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function (response) {
                if (response.status === 'success') {
                    location.reload();
                } else {
                    alert(response.message);
                }
            }
        });
    });
});