/**
 * common.js
 * Common scripts to be used throughout the site
 */

$(document).ready( function()
{

    /**
     *  Scroll up button
     */
    var scrollup        = $('.scrollup');
    var window_height   =  $(window).height();

    $(window).scroll( function(){
        if( $(window).scrollTop() > window_height){
            scrollup.addClass('visible');
        } else {
            scrollup.removeClass('visible');
        }
    });

    scrollup.click( function(){
        $('body, html').animate({ scrollTop: '0'});
    });

    /**
     *  Slideshow
     */
    var delay = 0;

    $('.fadein').each( function(){
        var _this_ = $(this);
        window.setTimeout( function(){
            $('.fadein__item', _this_).eq(0).addClass('active');
            window.setInterval( function(){
                fade('.fadein__item', _this_);
            }, 4000 );
        }, delay+=200 )
    });

    function fade(element, container){
        var items        = $(element, container);
        var items_number = items.length;
        var active_index = $('.active', container).index();
        var next_index   = active_index + 1 == items_number ? 0 : active_index + 1;
        var active       = items.eq(active_index);
        var next         = items.eq(next_index);
        active.removeClass('active');
        next.addClass('active');
    }

});
