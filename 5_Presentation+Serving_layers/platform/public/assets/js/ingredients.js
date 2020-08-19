
var ingredients = (function() {
    /*
        'on document ready' entry point
    */

    $(function() {

        $('input[type=radio]').click(function() {
            $(this).closest('.card').find('.ingredient-name').text($(this).val());
        });

        $('.discard-ingredient').on('click', function(e) {
            $(this).closest('.card').fadeOut(300, function() { $(this).remove(); });
        });

        $('.feedback-modal-submit').on('click', function(e) {

            let raw = $(this).closest('.modal').find('.feedback-raw').text();
            let ingredient = $(this).closest('.modal').find('.feedback-ingredient').val();
            let amount = $(this).closest('.modal').find('.feedback-amount').val();

            let id = $(this).closest('.modal').attr('id').split('-')[2]

            $('#button-feedback-' + id).removeClass('btn-outline-secondary').addClass('btn-success').attr('disabled', 'disabled');

            $.ajax({
                type: 'POST',
                url: '/ingredient/ner-feedback',
                data: {
                    'raw': raw,
                    'ingredient': ingredient,
                    'amount': amount
                },
                dataType: 'json' // response
            })
            .done(function(data) {
                // done :-)                
            })
            .fail(function(jqxhr, textStatus, error) {
                console.log('AJAX error, sorry :-/');
            });
        });
    });

    /*
    // exposes the following functions
    return {

    };
    */
})(jQuery);
