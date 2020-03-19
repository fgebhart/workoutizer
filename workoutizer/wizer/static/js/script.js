var greenIcon = new L.Icon({
    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

var redIcon = new L.Icon({
    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
});

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

$(document.documentElement).keyup(function (event) {
    if (event.keyCode === 72) {                 // h
        window.location.href = '/';
    } else if (event.keyCode === 83) {          // s
        window.location.href = '/sports';
    } else if (event.keyCode === 65) {          // a
        window.location.href = '/add-activity';
    } else if (event.keyCode === 188) {         // ,
        window.location.href = '/settings';
    }
});
