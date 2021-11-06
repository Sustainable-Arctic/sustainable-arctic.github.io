/* 
Google Maps
*/
var maps = '';
var center;

function initialize() {
    var mapOptions = {
      zoom: 16,
      center: new google.maps.LatLng(13.758468, 100.567481),
      scrollwheel: false
    };
  
    maps = new google.maps.Map(document.getElementById('map-canvas'),  mapOptions);

    google.maps.event.addDomListener(maps, 'idle', function() {
        calculateCenter();
    });
  
    google.maps.event.addDomListener(window, 'resize', function() {
      maps.setCenter(center);
    });
}

function calculateCenter() {
  center = maps.getCenter();
}

function loadGoogleMap(){
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://maps.googleapis.com/maps/api/js?v=3.exp&sensor=false&' + 'callback=initialize';
    document.body.appendChild(script);
}

/* HTML document is loaded. DOM is ready. 
-------------------------------------------*/
$(function(){
  /* FlexSlider */
  $('.flexslider').flexslider({
      animation: "fade",
      directionNav: false
  });

  $(".rotate").textrotator();

  new WOW().init();

  loadGoogleMap();
});