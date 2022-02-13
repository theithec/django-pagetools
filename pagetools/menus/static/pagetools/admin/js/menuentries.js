(function($){
  $(document).ready(function() {
    var $nest = $('.sortable').nestedSortable({
            handle: 'div',
            items: 'li',
            toleranceElement: '> div',
      });
    $('input[type="submit"]').click(function(){
      $("[name='entry-order']").val($nest.sortable("serialize"));
    });
  });
})(jQuery); // "our" jquery, not grp.jQuery
