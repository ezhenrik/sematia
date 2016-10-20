

var segtok = ''

var getSegtok = function() {
    return segtok
}

var haveTransformation = function(xml) {
    xml = $(xml)
    xml.find('treebank').attr('sematiaID', $('.edit-hand').attr('data-id'))
    $('.tb-result').text(xml[0].outerHTML)
    $('#put_treebank .save').removeClass('disabled')
}

var getTransformation = function(text) {
    let endpoint = 'https://services.perseids.org/llt/segtok',
        params = {
        'xml': 'false',
        'inline': 'true',
        'splitting': 'true',
        'merging': 'false',
        'shifting': 'false',
        'remove_node': ['teiHeader', 'head', 'speaker', 'note', 'ref'],
        'go_to_root': 'TEI',
        'ns': 'http://www.tei-c.org/ns/1.0',
        'text': text
    }
    $.ajax({
        method: 'POST',
        url: endpoint,
        data: params,
        dataType: 'text',
        success: function(data) {
            segtok = data
            $('body').trigger("llt-transform");
        }
    });
}

var getLanguage = function() {
    return $('#langForm input[name=lang]:checked').attr('val')
}

var getCollection = function() {
    return $('#langForm input[name=lang]:checked').attr('data-collection')
}

$(document).ready(function() {
    $('body').ctsXSLT("llt.segtok_to_tb", {
        "endpoint" : '/static/xslt/segtok_to_tb.xsl',
        "xml" : getSegtok,
        "driver" : {
            "e_lang" : function() { return getLanguage() },
            "e_dir" : function() { return 'ltr'},
            "e_attachtoroot" : function() { return false},
            "e_collection" : function() {return getCollection() },
            "e_agenturi" : function() { return 'https://services2.perseids.org/llt/segtok'}
        },
        "trigger" : "llt-transform",
        "callback" : function(data) {
            haveTransformation(data)
        }
    });
})


