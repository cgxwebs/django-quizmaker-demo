let CREATE_CTR = 0;
let CREATE_SEQ = 0;

$(function() {
    CREATE_CTR = $('#frm-list .q-row').length;
    CREATE_SEQ = CREATE_CTR;

    $('#q-add-another').on('click', function() {
        if (CREATE_CTR >= CONFIG['ROWS_MAX']) {
            alert('Maximum rows reached');
            return false;
        }
        let cln = $('#frm-row-origin').clone(true).removeAttr('id');
        // cln.find('.q-ctrl').val('');
        for (let w of ['question', 'answer', 'pics', 'clue', 'ref', 'choices', 'video']) {
            const new_attr = CONFIG['MODE'] + '-' + CREATE_SEQ + '-' + w;
            cln.find('#id_'+CONFIG['MODE']+'-0-'+w).attr('id', 'id_'+new_attr).attr('name', new_attr).val('');
        }
        cln.find('.q-opts').show();
        cln.find('.q-thumbs').detach();
        cln.find('.q-error').html('');
        cln.appendTo($('#frm-list'));
        CREATE_CTR++;
        CREATE_SEQ++;
        $('#id_'+CONFIG['MODE']+'-TOTAL_FORMS').val(CREATE_SEQ);
        return false;
    })

    $('.q-remove-row').on('click', function() {
        if (CREATE_CTR <= CONFIG['ROWS_MIN']) {
            alert('Minimum rows reached');
            return false;
        }
        let row = $(this).parents('.q-row');
        if (row.attr('id') === undefined) {
            row.remove();
            CREATE_CTR--;
        }
        $('#id_'+CONFIG['MODE']+'-TOTAL_FORMS').val(CREATE_SEQ);
        return false;
    });

    if (CONFIG['MODE'] !== undefined) {
        if (CREATE_CTR < CONFIG['ROWS_MIN']) {
            for (let i = 0; i <= CONFIG['ROWS_MIN'] - CREATE_CTR; i++) {
                $('#q-add-another').trigger('click');
            }
        }
        $('#id_'+CONFIG['MODE']+'-INITIAL_FORMS').val('0');

        $('.q-save').on('click', function() {
            let flag = true;
            for (let i of $('input, textarea, select')) {
                if (false === i.reportValidity()) {
                    flag = false; break;
                }
            }
            if (flag) {
                $('#content_wrapper').hide();
                $('<div><h1>Saving... Please wait</h1></div>').appendTo('#main_wrapper');
            }
        });
    }

    $('.mcq-ans-item').draggable({
        snap: '.mcq-canvas-t',
        revert: 'invalid',
        helper: 'clone',
        containment: 'document'
    });
    $('.mcq-canvas-t, #mcq-ans').droppable({
        drop: function(event, ui) {
            let item = $(ui.draggable);
            let target = $(this);
            const is_answer = target.attr('id') !== 'mcq-ans';
            const last_target = item.data('last_target');
            item.fadeOut(function() {
                item.removeAttr('style');
                item.appendTo(target);
                if (last_target !== undefined && last_target.length > 0) {
                    $('input[name=' + item.data('last_target') + ']').val('');
                }
                if (is_answer) {
                    let target_input = target.find('.sel_answer');
                    target_input.val(item.text());
                    item.data('last_target', is_answer ? target_input.attr('name') : '');
                } else {
                    item.data('last_target', '');
                }

            })
        }
    });
})