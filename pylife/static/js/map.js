var cityNameList = [
    "Tierra Robada",
    "Bone County",
    "Las Venturas",
    "San Fierro",
    "Red County",
    "Whetstone",
    "Flint County",
    "Los Santos"
]

var icon_31 = L.icon({ iconUrl: './static/icons/Icon_31.png', iconSize: [16, 16] });
var icon_32 = L.icon({ iconUrl: './static/icons/Icon_32.png', iconSize: [16, 16] });

var img = [
    6000,  // original width of image (here from `example/karta.jpg`)
    6000   // original height of image
];

// create the map
var map = L.map('map');

// assign map and image dimensions
var rc = new L.RasterCoords(map, img);

// layer groups
var layers = {
    houses: L.featureGroup(),
    jobs: L.featureGroup()
}

// set max zoom Level (might be `x` if gdal2tiles was called with `-z 0-x` option)
map.setMaxZoom(rc.zoomLevel());

// all coordinates need to be unprojected using the `unproject` method
// set the view in the lower right edge of the image
map.setView(rc.unproject([3000, 3000]), 4);

// the tile layer containing the image generated with `gdal2tiles --leaflet -p raster -w none <img> tiles`
L.tileLayer('./tiles/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://panel.pylife.pl/">Play Your Life</a>, Imagery &copy; <a href="http://ian-albert.com/games/grand_theft_auto_san_andreas_maps/">IanAlbert.com</a>',
    noWrap: true
}).addTo(map);

var zones = L.featureGroup();

// load zones
$.getJSON('./points/zones', function(json) {
    json.data.forEach(function(zone) {
        var points = zone.points.map(function(point) {
            if (point.x) {
                return rc.unproject([point.x, point.y]);
            } else {
                return point.map(function(point) {
                    return rc.unproject([point.x, point.y]);
                });
            }
        });

        var polygon = L.polygon(points, { id: zone.id, name: zone.name });
        polygon.addTo(zones)
    });
});

map.on('click', function(event) {
    // to obtain raster coordinates from the map use `project`
    var coord = rc.project(event.latlng)

    // to set a marker, ... in raster coordinates in the map use `unproject`
    var marker = L.marker(rc.unproject(coord)).addTo(map)

    // current marker location
    var zoneName = null, cityName = null;

    // find closest zone and city name
    zones.eachLayer(function(layer) {
        if (layer.getBounds().contains(event.latlng)) {
            if (cityNameList.includes(layer.options.name)) {
                cityName = layer.options.name;
            } else {
                zoneName = layer.options.name;
            }
        }
    });

    // add popup to marker with location name
    marker.bindPopup((zoneName ? "<b>" + zoneName + "</b><br />" : "") + cityName).openPopup();
    marker.getPopup().on('remove', function() {
        map.removeLayer(marker);
    });
})


// load house markers
$.getJSON('./points/houses', function(json) {
    json.data.forEach(function(house) {
        L.marker(rc.unproject([house.x, house.y]), {icon: house.owner ? icon_32 : icon_31, id: house.id}).addTo(map);
    });
});

// show welcome modal
$(document).ready(function() {
    var audio = new Audio('./assets/Lot_nad_miastem.ogg');

    if (!localStorage.cookieConsent) {
        $('#welcome').modal('show');
        audio.play();
    }

    $('#togglemusic').click(function() {
        if (!audio.paused) {
            audio.pause();
        } else {
            audio.play();
        }
    });

    $('#accept').click(function() {
        $('#welcome').modal('hide');
        localStorage.cookieConsent = true;
    });
});
