$(window).on('entity:view:list', function () {
    // Move all topology-filters to separate tab
    $('#mainfilter .right-filter').parent('p')
                                     .detach().appendTo('#mainfilter > .right');
});
