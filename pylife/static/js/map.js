var icon_31 = L.icon({ iconUrl: './icons/Icon_31.png', iconSize: [16, 16] });
var icon_32 = L.icon({ iconUrl: './icons/Icon_32.png', iconSize: [16, 16] });

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

// load house markers
$.getJSON('./points/houses', function(json) {
    json.data.forEach(function(house) {
        L.marker(rc.unproject([house.x, house.y]), {icon: house.owner ? icon_32 : icon_31, id: house.id}).addTo(map);
    });
});

// show welcome modal
$(document).ready(function() {
    var audio = new Audio('./assets/Lot_nad_miastem.ogg');

    if (localStorage.cookieConsent == undefined) {
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
