(function($){
    $(document).ready(function(){
        $('#changelist-filter li').hide();
        $('#changelist-filter li.selected').show();
        $('#changelist-filter h3').click(function(){
            $(this).next().children('li').show();
        });
    });
})(django.jQuery);
