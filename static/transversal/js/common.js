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

    /**
     *  addMessage
     *  Create an asynchoronous django message. This method It's coupled to the current
     *  messages region template
     *
     *  @param {String} msg
     *  Text content of the message
     *  @param {String} tag
     *  Class modifier to be appended to resulting message implying its state
     *  (success, fail, warning, etc.)
     *
     *  @see templates/regions/messages.html
     */
    function addMessage(msg, tag){
        var messages = $('.messages-list');
        var message  = "<li class='messages-list__msg--" + tag + "'>" + msg + "</li>";
        messages.prepend(message);
    }

    /**
     *  curateContent
     *  Make an ajax GET request to make an API call to include/exclude
     *  related content
     *
     *  @param {HTMLElement} trigger
     *  HTML node that triggers the action. It has to contain to three
     *  data attributes to work properly.
     *  data-pk          : id of the related element
     *  data-contenttype : content-type of the related element
     *  data-action      : current action (add or remove)
     *
     *  @see templates/blocks/widget-curate.html
     *  @todo i18n
     */

    function curateContent(trigger){
        var action = trigger.attr('data-action');
        $.ajax({
            method: "GET",
            url: "/curate",
            data: {
                'pk'          : trigger.attr('data-pk'),
                'contenttype' : trigger.attr('data-contenttype'),
                'action'      : action,
            }
        }).done( function(data)
        {
            if(action=='add'){
                trigger.attr('data-action', 'remove');
                trigger.attr('class', 'curate-widget__button-remove--page');
                trigger.text('Remove this item from your list of curated content');
                addMessage('Content succesfully added to your list of curated contents', 'success');
                trigger.parent().parent().toggleClass('removed');
            } else {
                trigger.attr('data-action', 'add');
                trigger.attr('class', 'curate-widget__button-add--page');
                trigger.text('Add this item to your list of curated content');
                addMessage('Content succesfully removed from your list of curated contents', 'success');
                trigger.parent().parent().toggleClass('removed');
            }
        });
    }

    // Bind curateContent to its triggers
    $('#curate-button').click( function(){
        curateContent( $(this) );
    });

    // Lightbox
    $('.book__meta-image').click( function(){
        $(this).toggleClass('lightbox');
    });


});
