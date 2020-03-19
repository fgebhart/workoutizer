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

function get_sport(event, sports) {
    let event_as_int = Number(String.fromCharCode(event.which));
    if (event_as_int === 0) {
        event_as_int = sports.length;
    }
    console.log(event_as_int);
    return '/sport/' + sports[event_as_int - 1]
}

function go_to_page_with_key(event, sports) {
    if (event.keyCode === 72) {                 // h
        window.location.href = '/';
    } else if (event.keyCode === 83) {          // s
        window.location.href = '/sports';
    } else if (event.keyCode === 65) {          // a
        window.location.href = '/add-activity';
    } else if (event.keyCode === 188) {         // ,
        window.location.href = '/settings';
    } else if (event.keyCode === 48) {          // 0
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 49) {          // 1
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 50) {          // 2
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 51) {          // 3
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 52) {          // 4
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 53) {          // 5
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 54) {          // 6
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 55) {          // 7
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 56) {          // 8
        window.location.href = get_sport(event, sports);
    } else if (event.keyCode === 57) {          // 9
        window.location.href = get_sport(event, sports);
    }
}