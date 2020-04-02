// create the map
var map = L.map('map');

// assign map and image dimensions
var rc = new L.RasterCoords(map, [6000, 6000]);

// set max zoom Level (might be `x` if gdal2tiles was called with `-z 0-x` option)
map.setMaxZoom(rc.zoomLevel());

// all coordinates need to be unprojected using the `unproject` method
// set the view in the lower right edge of the image
map.setView(rc.unproject([3000, 3000]), 3);

// the tile layer containing the image generated with gdal2tiles.py
L.tileLayer('./tiles/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://panel.pylife.pl/">Play Your Life</a>, Imagery &copy; <a href="http://ian-albert.com/games/grand_theft_auto_san_andreas_maps/">IanAlbert.com</a>',
    noWrap: true
}).addTo(map);

// layer groups
var layers = {
    zones: L.featureGroup(),
    houses: L.featureGroup()
};

// remove markers that are outside view bounds to improve performance
map.on('zoomend moveend resize zoom move', function() {
    layers.houses.eachLayer(function(layer) {
        if (map.getBounds().contains(layer.getLatLng())) {
            map.addLayer(layer);
        } else {
            map.removeLayer(layer);
        }
    });
});


function formatDate(timestamp) {
    return dayjs(timestamp).format('YYYY-MM-DD HH:mm')
}


function getHouseIcon(house) {
    if (house.owner) {
        return L.icon({iconUrl: './static/icons/Icon_32.png', iconSize: [16, 16]});
    } else {
        return L.icon({iconUrl: './static/icons/Icon_31.png', iconSize: [16, 16]});
    }
}


function createZonePolygon(zone) {
    var points = zone.points.map(function(point) {
        if (point.x) {
            return rc.unproject([point.x, point.y]);
        } else {
            return point.map(function(point) {
                return rc.unproject([point.x, point.y]);
            });
        }
    });

    return L.polygon(points, {id: zone.id, name: zone.name});;
}


function createHouseMarker(house) {
    var popupText = '<dt>' + house.id  + '. ' + house.name + '</dt><dd>' + house.location + '</dd>';

    if (house.owner) {
        popupText += '<dt><i class="fa fa-user fa-fw"></i> Właściciel:</dt><dd>' + house.owner + '</dd>' +
            '<dt><i class="fa fa-money fa-fw"></i> Cena:</dt><dd>' + house.price + '€ za dobę</dd>' +
            '<dt><i class="fa fa-calendar fa-fw"></i> Wynajęty do:</dt><dd>' + formatDate(house.expiry) + '</dd>';
    } else {
        popupText += '<dd>Do wynajęcia!<dd>' +
            '<dt><i class="fa fa-money fa-fw"></i> Cena:</dt><dd>' + house.price + '€ za dobę</dd>';
    }

    popupText += '<a href="http://panel.pylife.pl/domy/' + house.id + '" target="_blank">Sprawdź dom w panelu</a>';

    var marker = L.marker(rc.unproject([house.x, house.y]), {id: house.id, location: house.location, icon: getHouseIcon(house)});
    marker.bindPopup(L.responsivePopup().setContent(popupText));

    return marker;
}


function getZoneById(zoneId) {
    var zone = null;
    layers.zones.eachLayer(function(layer) {
        if (layer.options.id === zoneId) {
            zone = layer;
            return;
        }
    })

    return zone;
}


function getHousesInBounds(bounds) {
    var count = 0;
    layers.houses.eachLayer(function(layer) {
        if (bounds.contains(layer.getLatLng())) {
            count += 1;
            return;
        }
    })

    return count;
}


map.on('click', function(event) {
    // to obtain raster coordinates from the map use `project`
    var coord = rc.project(event.latlng)

    // to set a marker, ... in raster coordinates in the map use `unproject`
    var marker = L.marker(rc.unproject(coord)).addTo(map)

    // find closest zone and city name
    $.getJSON('./lookup?x=' + parseInt(coord.x) + "&y=" + parseInt(coord.y), function(json) {
        // add popup to marker with location name
        if (json.city_name) {
            popup = marker.bindPopup((json.zone_name ? "<b>" + json.zone_name + "</b><br />" : "") + json.city_name).openPopup();
        } else {
            popup = marker.bindPopup("Brak lokalizacji").openPopup();
        }

        marker.getPopup().on('remove', function() {
            marker.remove();
        });
    });
})

// load zone polygons
$.getJSON('./points/zones', function(json) {
    json.data.forEach(function(zone) {
        createZonePolygon(zone).addTo(layers.zones)
    });
});

// load house markers
$.getJSON('./points/houses', function(json) {
    json.data.forEach(function(house) {
        var marker = createHouseMarker(house).addTo(layers.houses);
        if (map.getBounds().contains(marker.getLatLng())) {
            marker.addTo(map);
        }
    });
});


function setCookie(name, value, expiry) {
    var date = new Date();
    date.setTime(date.getTime() + (expiry * 24 * 60 * 60 * 1000));
    document.cookie = name + "=" + value + ";expires="+ date.toUTCString() + ";path=/";
}


function getCookie(name) {
    var prefix = name + "=";
    var decodedCookie = decodeURIComponent(document.cookie);

    var ca = decodedCookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }

        if (c.indexOf(prefix) == 0) {
            return c.substring(prefix.length, c.length);
        }
    }

    return null;
}


// show welcome modal
$(document).ready(function() {
    if (!getCookie("cookieconsent_status")) {
        $('#welcome').modal('show');
    }

    $('#accept').click(function() {
        $('#welcome').modal('hide');
        setCookie("cookieconsent_status", "dismiss", 365);
    });
});