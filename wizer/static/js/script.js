
var greenIcon = new L.Icon({
    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
    iconSize: [18, 28],
    iconAnchor: [9, 28],
    popupAnchor: [1, -34],
});

var redIcon = new L.Icon({
    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    iconSize: [18, 28],
    iconAnchor: [9, 28],
    popupAnchor: [1, -34],
});

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();

    // close right sidebar if clicked anywhere
    $(window).click(closeSidebar);
    // stop propagation if this element is clicked so close sidebar is not triggered
    $('#sidebar').click(function (event) {
        event.stopPropagation();
    });
    $('#open-sidebar').click(openSidebar);
});

function openSidebar(event) {
    $("#sidebar").addClass('sidebar_opened');
    $('#open-sidebar').hide();
    // stop propagating so closeSidebar is not triggered right away
    event.stopPropagation();
}

function closeSidebar() {
    $("#sidebar").removeClass('sidebar_opened');
    // we show the open button after the sidebar is not visible (css transition time is 0.5s)
    if (window.innerWidth <= 992) {
        setTimeout(function () {
            $('#open-sidebar').show();
        }, 500);
    }
}