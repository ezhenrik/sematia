

var segtok = ''
var endpoint = 'http://services.perseids.org/llt/segtok'

var getSegtok = function() {
    return segtok
}

var haveTransformation = function(xml) {
    console.log(xml)
    return xml
}

var getTransformation = function(text) {
    $.ajax({
        url: endpoint + '?xml=false&inline=true&splitting=true&merging=false&shifting=false&remove_node[]=teiHeader&remove_node[]=head&remove_node[]=speaker&remove_node[]=note&remove_node[]=ref&go_to_root=TEI&ns=http%3A%2F%2Fwww.tei-c.org%2Fns%2F1.0&text='+text,
        dataType: 'text',
        success: function(data) {
            segtok = data
            console.log(segtok)
            $('body').trigger("llt-transform");
        }
    });
}

$(document).ready(function() {
    $('body').ctsXSLT("llt.segtok_to_tb", {
        "endpoint" : '/static/xslt/segtok_to_tb.xsl',
        "xml" : getSegtok,
        "driver" : {
            "e_lang" : function() { return 'grc'},
            "e_dir" : function() { return 'ltr'},
            "e_attachtoroot" : function() { return false},
            "e_collection" : function() { return 'urn:cite:perseus:grctb'},
            "e_agenturi" : function() { return 'http://services2.perseids.org/llt/segtok'}
        },
        "trigger" : "llt-transform",
        "callback" : function(data) {
            haveTransformation(data)
        }
    });
})

