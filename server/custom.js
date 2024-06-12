// remove the show class to the div id "sidebar" is the screen size is less than 768px

$(window).resize(function() {
    if ($(window).width() < 768) {
        $('#sidebar').removeClass('show');
    }
});