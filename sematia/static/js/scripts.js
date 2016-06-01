/* Modals */
function clearModal($modal) {
    $modal.find('.alerts, .messages').addClass('hidden');
    $modal.find('.alert-content').text('');
    $modal.find('input[type="text"]').not('.static').val('');
    $modal.find('textarea').not('.static').val('');
    $modal.find('.confirm').removeClass('confirm').text('Delete')
}

function initModal($modal) {
    $modal.find('.alerts').addClass('hidden');
    $modal.find('.messages .alert-content').text('Please wait...');
    $modal.find('.messages').removeClass('hidden');
}

function finalizeModal($modal, result) {
    $modal.find('.messages').addClass('hidden');
    if (result.status != 'ok') {
        $modal.find('.alerts .alert-content').text(result.message);
        $modal.find('.alerts').removeClass('hidden');
    } else {
        $modal.find('.alerts').addClass('hidden');
        $modal.find('.messages .alert').removeClass('alert-info').addClass('alert-success');
        $modal.find('.messages .alert-content').text('Success! Please wait...');
        $modal.find('.messages').removeClass('hidden');
        location.reload();
    }
}

/* Ajax */
function ajaxJson(method, data) {
    var dataSettings = (typeof data == "object" && data.constructor.name == "FormData")
        ? {processData:false,contentType:false} : {},

        retval,
    
        settings = {
        type: 'POST',
        url: $SCRIPT_ROOT + method,
        dataType: 'json',
        data:data,
        async:false,
        success: function(data) { 
            if (data.status != 'ok') {
                retval = {'status':'error', 'message':data.message};
            } else {
                retval = data;
            }
        }
    }
    $.ajax($.extend(settings, dataSettings));
    return retval;
}

/* Ajax wrapper */
function processAjaxRequest(el, method, data) {
    $modal = el.closest('div.modal');
    initModal($modal);
    finalizeModal($modal, ajaxJson(method, data));
}

/* Text selection */
function selectText(element) {
    var range, selection;
    var doc = document;
    var text = element[0];
    if (doc.body.createTextRange) {
        range = document.body.createTextRange();
        range.moveToElementText(text);
        range.select();
    } else if (window.getSelection) {
        selection = window.getSelection();        
        range = document.createRange();
        range.selectNodeContents(text);
        selection.removeAllRanges();
        selection.addRange(range);
    }
}

/* Get text values from the transcription window */
function getTextValues(el, handno) {
    textcontent = '<div class="part"><span class="glyphicon glyphicon-briefcase copy"></span>';
    currentHand = 1;
    el.find('*:not(:has(*), .lb, .delete, .textpart-indicator)').each(function() {


        if ($(this).is('.handShift')) {
            currentHand++;
        }

        var a = (currentHand == handno);

        if (
            !$(this).parents('.delete').length 
            && !$(this).parents('.manualDisSelection').length 
            && !$(this).parents('.manualDeepParent').length

            ||
            (
                ($(this).parents('.manualDeepParent').length && $(this).parents('.manualSelection').length) &&

                  (
                  $(this).closest('.choice, .app').children('.manualSelection').length ||

                  (!$(this).closest('.choice, .app').children('.manualSelection').length && 
                    !$.contains($(this).closest('.choice, .app')[0], $(this).closest('.delete')[0]))
                   
                ) 
            )

            ) {

            if ($(this).closest('.modified').length && !$(this).parents('.modified').last().is('.processed')) {
                var mod = $(this).closest('.modified');
                textcontent += a ? mod.data('layerValue') : '';
                mod.addClass('processed');
            }

            else if ($(this).is('.modified')) {
                textcontent += a ? mod.data('layerValue') : '';
            }

            else if ($(this).is('.gap')) {
                textcontent += a ? 'G' : '';
            }

            else if (!$(this).parents('.modified').last().is('.processed') && !$(this).is('.handShift')) {
                textcontent += a ? $(this).text() : '';
            } 
        }

    });
    el.find('*').removeClass('processed');
    textcontent += '</div>';
    return textcontent;
}

/* Format windows according to layer type */
function formatLayer(type, paths, handno) {
    var error = false;
    if (!error) {
        $('.loader').show();
        var el = $('.originaltext').clone(true);

        var tags = [];
        var mytags = ['textpart-indicator', 'text','tail','modified','delete', 'ab', 'div', 'manualSelection', 'manualDisSelection', 'originaltext'];
        
        el.find('*').each(function() {
            var eltags = $(this).attr('class').split(/\s+/);
            
            for (var i in eltags) {
                if (tags.indexOf(eltags[i]) < 0 && mytags.indexOf(eltags[i]) < 0) {
                    tags.push(eltags[i]);
                }
            }
        })
        tags = tags.sort();
        tagHtml = '<ul class="list-group">';
        for (tag in tags) {
          tagHtml += '<li class="'+tags[tag]+' list-group-item"><span>'+tags[tag]+'</span></li>';
        }
        tagHtml += '</ul>';
        $('.elements').html(tagHtml);

        el2 = generalFormatting(el);
        el3 = enableHand(el2, handno);
        enableLayer(type, el2, paths, handno);
        
    } else {
        $('.alerts').removeClass('hidden');
    }
    $('.loader').hide();
    $('.messages').addClass('hidden');
}

/* Transcription window: Common formatting */
function generalFormatting(el) {
    el.add(el.find('*')).each(function() {
        if ($(this).attr('data-type') && $(this).attr('data-type') == 'textpart') {
            var n = $(this).data('n');
            $(this).prepend('<span class="textpart-indicator">Part '+n+'</span>');
        }
    })
    
    // Gaps
    el.find('.gap').each(function() {
        var w = $(this).data('quantity');
        if (w) {
            $(this).width(w * 10);
        }
        $(this).html('');
    });

    // Handshift
    el.find('.handShift').each(function() {
        $(this).html('HS');
    });

    // Lbs
    el.find('.lb').each(function() {
        $(this).text($(this).data('n'))

        if ($(this).data('break') == 'no') {
            $(this).prev('.text').text($(this).prev('.text').text().replace(/[ \n]+$/,''));
        } else {
            $(this).prev('.text').text($(this).prev('.text').text().replace(/\s*$/," "));
        }
    });

    return el;
}

/* Enable hand */
function enableHand(el, handno) {
    currentHand = 1;
    var ti = 0;
    var si = 'None';
    var li = 'None';

    // Fade effect
    el.find('*:not(.ab, .div)').each(function() {
        if ($(this).is('.handShift')) {
            currentHand++;
        }
        if (currentHand == handno) {
            if (si == 'None') {
                si = ti;
            }
            $(this).addClass('activeHand');
        } else {
            if (si != 'None' && li == 'None') {
                li = ti;
            }
        }
        ti++;

    });

    if (li == 'None') {
        li = ti;
    }

    var ti = 0;
    el.find('*:not(.ab, .div)').each(function() {
        if (ti < si) {
            if (si - ti < 30) {
                $(this).css({'opacity': 1-((si-ti)/30), 'color':'#ddd', 'border':'none'});
            } else {
                $(this).css('display', 'none');
            }
        } else if (ti > li) {
            if (ti - li < 30) {
                $(this).css({'opacity': 1-((ti-li)/30), 'color':'#ddd', 'border':'none'});
            } else {
                $(this).css('display', 'none');
            }
        }
        ti++;
    })
}

/* Transcription window: Enable layer formatting */
function enableLayer(layer, el, paths, handno) {

    var clone = el;

    if (layer == "original" || layer == "standard" || layer == "variation") {

        // subst
        clone.find('.subst').each(function() {
            $(this).find('.del').remove();
        });

        // app
        clone.find('.app').each(function() {
           /* if ($(this).is(':not(.lem)') && !$(this).closest('.lem').length) {
                $(this).remove();
            }*/
          $(this).find('>:not(.lem)').addClass('delete');
        });

    }

    // Orig layer
    if (layer == "original" || layer == "variation") {

        // ex
        clone.find('.ex').each(function() {
            $(this).addClass('modified');
            $(this).data('layerValue', 'A');
        });

        // supplied
        clone.find('.supplied').each(function() {
          var replaceString = 'SU';
          if ($(this).attr('data-reason') == 'omitted') {
            replaceString = 'OM';
          }
          var text = $(this).text();
          var text = text.replace(/([“”—\"‘’\.,:;··;\?!\[\]{}\-])/g, " $1 ");
          var text = text.replace(/([ ]{2,})/g, " ");
          var text = text.replace(/[^\s^\.]+/g, replaceString);
          $(this).addClass('modified');
          $(this).data('layerValue', text);
        });

        // choice
        clone.find('.choice').each(function() {
          $(this).find('.reg').addClass('delete');
          $(this).find('.corr').addClass('delete');
        });

    // Standard layer
    } else if (layer == "standard") {

        // surplus
        clone.find('.surplus').each(function() {
            $(this).addClass('modified');
            $(this).data('layerValue', 'SR');
        });

        // choice
        clone.find('.choice').each(function() {
            $(this).find('.orig').addClass('delete');
            $(this).find('.sic').addClass('delete');
        });
    }

    if (paths != '' && paths != 'None') {
        console.log(paths);
        paths =  $.parseJSON(paths);
        for (i in paths) {
            path = paths[i];
            el = clone.find('>'+path);
            deepparent = el.parents('.choice,.app').last();
            deepparent.toggleClass('manualDeepParent');
            el.parent().find('> * ').removeClass('manualSelection').addClass('manualDisSelection');
            el.removeClass('manualDisSelection').addClass('manualSelection');
        }
    }

    $('.editorview').empty().html(clone.find('> *'));

    var textContent = getTextValues($('.editorview'), handno);
    $('.text-content').html(textContent);
}

/* Transcription window: Save custom paths */
function saveLayer(id, handno) {
    custompaths = [];
    $('.editorview .manualSelection').each(function() {
        var elem = $(this);
        var path = elem.getPath();
        custompaths.push(path);
    })

    var data = {
        id: id,
        paths:JSON.stringify(custompaths)
    };

    result = ajaxJson('/save_paths', data);

    var textContent = getTextValues($('.editorview'), handno);
    $('.text-content').html(textContent);
}

/* Manual selection helper */
jQuery.fn.getPath = function () {
    if (this.length != 1) throw 'Requires one element.';

    var path, node = this;
    while(!$(node).is('.editorview')) {
        var realNode = node[0], name = realNode.localName;
        if (!name) break;
        name = name.toLowerCase();

        var parent = node.parent();

        var siblings = parent.children(name);
        if (siblings.length > 1) { 
            name += ':eq(' + siblings.index(realNode) + ')';
        }

        path = name + (path ? '>' + path : '');
        node = parent;
    }

    return path;
};