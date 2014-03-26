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


});