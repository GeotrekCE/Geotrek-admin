/*
    Telephasic 1.1 by HTML5 UP
    html5up.net | @n33co
    Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
*/

skel.init({
    /*
        Docs @ http://skeljs.org/docs
    */
    prefix: 'css/style',
    resetCSS: true,
    useOrientation: true,
    boxModel: 'border',
    breakpoints: {
        'n1': { range: '*', containers: 1200, grid: { gutters: 50 } },
        'n2': { range: '-1320', containers: 960, grid: { gutters: 40 } },
        'n3': { range: '-1300', containers: 'fluid', grid: { gutters: 40 } },
        'n4': { range: '-820', lockViewport: true, containers: 'fluid', grid: { gutters: 30, collapse: 1 } },
        'n5': { range: '-640', lockViewport: true, containers: 'fluid', grid: { gutters: 30, collapse: 2 } },
        'n6': { range: '-568', lockViewport: true, containers: 'fluid', grid: { gutters: 15, collapse: 2 } }
    }
},{
    /*
        Docs @ http://skeljs.org/panels/docs
    */
    panels: {
        panels: {
            navPanel: {
                breakpoints: 'n6',
                position: 'top',
                size: '75%',
                /*
                    Note: Since there's no explicit "Home" link in the nav I've manually added one to the top of the navPanel.
                */
                html: '<a href="index.html" class="link depth-0">Home</a><div data-action="navList" data-args="nav"></div>'
            }
        },
        overlays: {
            navButton: {
                breakpoints: 'n6',
                position: 'top-center',
                width: 100,
                height: 50,
                html: '<div class="toggle" data-action="togglePanel" data-args="navPanel"></div>'
            }
        }
    }
});

jQuery.fn.n33_scrolly = function() {            
    var bh = jQuery('body,html'), t = jQuery(this);

    t.click(function(e) {
        var h = jQuery(this).attr('href'), target;

        if (h.charAt(0) == '#' && h.length > 1 && (target = jQuery(h)).length > 0)
        {
            var pos = Math.max(target.offset().top, 0);
            e.preventDefault();
            bh
                .stop(true, true)
                .animate({ scrollTop: pos }, 'slow', 'swing');
        }
    });
    
    return t;
};

// scrollzer
jQuery.n33_scrollzer = function(ids, userSettings) {

    var top = jQuery(window), doc = jQuery(document);
    
    // Settings
    var settings = jQuery.extend({
        activeClassName:    'active',
        suffix:             '-link',
        pad:                50,
        firstHack:          false,
        lastHack:           false
    }, userSettings);

    // Variables
    var k, x, o, l, pos;
    var lastId, elements = [], links = jQuery();

    // Build elements array
    for (k in ids)
    {
        o = jQuery('#' + ids[k]);
        l = jQuery('#' + ids[k] + settings.suffix);
    
        if (o.length < 1
        ||  l.length < 1)
            continue;
        
        x = {};
        x.link = l;
        x.object = o;
        elements[ids[k]] = x;
        links = links.add(l);
    }

    // Resize event (calculates start/end values for each element)
    var resizeTimerId, resizeFunc = function() {
        var x;
        
        for (k in elements)
        {
            x = elements[k];
            x.start = Math.ceil(x.object.offset().top) - settings.pad;
            x.end = x.start + Math.ceil(x.object.innerHeight());
        }
        
        top.trigger('scroll');
    };
    
    top.resize(function() {
        window.clearTimeout(resizeTimerId);
        resizeTimerId = window.setTimeout(resizeFunc, 250);
    });

    // Scroll event (checks to see which element is on the screen and activates its link element)
    var scrollTimerId, scrollFunc = function() {
        links.removeClass('scrollzer-locked');
    };

    top.scroll(function(e) {
        var i = 0, h, found = false;
        pos = top.scrollTop();

        window.clearTimeout(scrollTimerId);
        scrollTimerId = window.setTimeout(scrollFunc, 250);
        
        // Step through elements
        for (k in elements)
        {
            if (k != lastId
            &&  pos >= elements[k].start
            &&  pos <= elements[k].end)
            {
                lastId = k;
                found = true;
            }
            
            i++;
        }
            
        // If we're using lastHack ...
        if (settings.lastHack
        &&  pos + top.height() >= doc.height())
        {
            lastId = k;
            found = true;
        }
            
        // If we found one ...
        if (found
        &&  !links.hasClass('scrollzer-locked'))
        {
            links.removeClass(settings.activeClassName);
            elements[lastId].link.addClass(settings.activeClassName);
        }
    });
    
    // Initial trigger
    top.trigger('resize');
};

$(document).ready(function() {

    $(".owl-carousel").owlCarousel({

        // navigation : true, // Show next and prev buttons
        slideSpeed : 300,
        paginationSpeed : 400,
        singleItem: true,
        autoPlay: true

        // "singleItem:true" is a shortcut for:
        // items : 1,
        // itemsDesktop : false,
        // itemsDesktopSmall : false,
        // itemsTablet: false,
        // itemsMobile : false

    });

    $("#footer-wrapper form").on('submit', function(event) {
        event.preventDefault();

        var name = $(this).find('[name="name"]').val();
        var email = $(this).find('[name="email"]').val();

        $('input').removeClass('error');

        var nameIsEmpty = (!!name == "");
        if (nameIsEmpty) {
            $(this).find('[name="name"]').addClass('error');
        }

        var emailIsEmpty = (!!email == "");
        if (emailIsEmpty) {
            $(this).find('[name="email"]').addClass('error');
        }

        if (nameIsEmpty || emailIsEmpty) {
            $("#footer-wrapper .form-errors").show();
            $("#footer-wrapper .confirmed").hide();
            return false;
        }

        $.ajax({
          dataType: 'jsonp',
          url: "http://getsimpleform.com/messages/ajax?form_api_token=e81d577ce1527ee5f3cd7ecc6208826f",
          data: {
            name: name,
            email: email,
            phone: $(this).find('[name="phone"]').val(),
            message: $(this).find('[name="message"]').val()
          }
        }).done(function() {
            $("#footer-wrapper .confirmed").show();
            $("#footer-wrapper .form-errors").hide();
            $('input').removeClass('error');
            $('#contact-form [name]').val('');
        });

    });

    // Snippet from http://css-tricks.com/snippets/jquery/smooth-scrolling/
    $('a[href*=#]:not([href=#])').click(function() {
        if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
            var target = $(this.hash);
            target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
            if (target.length) {
                $('html,body').animate({
                  scrollTop: target.offset().top
                }, 1000);
            return false;
          }
        }
    });


    // Reveal CSS animation
    $(window).scroll(function() {
        $('.animated').each(function(){
        var elemPos = $(this).offset().top;

        var topOfWindow = $(window).scrollTop();
            if (elemPos < topOfWindow+400) {
                $(this).addClass("revealed");
            }
        });
    });

    //jQuery('.scrolly').n33_scrolly();

    // Initialize nav
    var $nav_a = jQuery('#nav a');

    // Scrollyfy links
    $nav_a
        .click(function(e) {

            var t = jQuery(this),
                href = t.attr('href');
            
            if (href[0] != '#')
                return;
            
            e.preventDefault();
            
            // Clear active and lock scrollzer until scrolling has stopped
                $nav_a
                    .removeClass('active')
                    .addClass('scrollzer-locked');
        
            // Set this link to active
                t.addClass('active');
        
        });

// Initialize scrollzer
    var ids = [];
    
    $nav_a.each(function() {
        
        var href = jQuery(this).attr('href');
        
        if (href[0] != '#')
            return;
    
        ids.push(href.substring(1));
    
    });
    
    jQuery.n33_scrollzer(ids, { pad: 200, lastHack: true });


});