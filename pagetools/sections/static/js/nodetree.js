$(document).ready(function(){
    function load_pagenodes(slug){
        var url = admin_pagenodesurl.replace('__SLUG__', slug);
        $.ajax({
            url: url,
            success: function(data, textStatus, jqXHR){
                console.log("D", data);
               content = data.content; //hasOwnProperty('content') 
               $("#pagenodes").replaceWith(content);
               $("#pagenodes").bonsai({'expandAll':true});        
            }
        });
    }
    $('#pagenode_page_chooser').change(function(evt){
        load_pagenodes(this.value);
    });
    var selText = $('#pagenode_page_chooser option:selected').text();
    if (selText && selText != ""){
        load_pagenodes(selText);
    }
});
