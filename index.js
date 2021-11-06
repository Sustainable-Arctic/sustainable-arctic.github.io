// This example creates a simple polygon representing the Bermuda Triangle.
// When the user clicks on the polygon an info window opens, showing
// information about the polygon's coordinates.
//import {requirejs,require} from '.require.js';

let map;
let infoWindow;
var jsonFile = {
    "leftTopGeoPos": [
      17.486770847915672,
      66.14555609777774
    ],
    "hexGridResolution": [
      {
        "width": 2,
        "height": 2
      }
    ],
    "cellWidthMeters": 1000,
    "data": [
        {
            "x": 0,
            "y": 0,
            "temp":
            {
                "min": -200,
                "max": 1000,
                "mean": 500,
                "std": 1000
            },
            "speed":
            {
                "min": -300,
                "max": 2000,
                "mean": 800,
                "std": 25
            }   
        }, {
            "x": 1,
            "y": 0,
            "temp":
            {
                "min": -200,
                "max": 1000,
                "mean": 500,
                "std": 1000
            },
            "speed":
            {
                "min": -300,
                "max": 2000,
                "mean": 800,
                "std": 25
            }
        }
    ]
}  
class Hex {

    constructor(center_x, center_y) 
    {
        this.center_x = center_x;
        this.center_y = center_y;
        let width = 0.25;
        let distortion = 3;

        this.triangleCoords = [
            { lng: this.center_x - 1/2*width*distortion, lat: this.center_y - width },
            { lng: this.center_x + 1/2*width*distortion, lat: this.center_y - width },
            { lng: this.center_x + width*distortion, lat: this.center_y},
            { lng: this.center_x + 1/2*width*distortion, lat: this.center_y + width },
            { lng: this.center_x - 1/2*width*distortion, lat: this.center_y + width },
            { lng: this.center_x - width*distortion, lat: this.center_y}
        ];
    }

    draw() {
        const bermudaTriangle = new google.maps.Polygon({
            paths: this.triangleCoords,
            strokeColor: "#FF0000",
            strokeOpacity: 0.8,
            strokeWeight: 3,
            fillColor: "#FF0000",
            fillOpacity: 0.35,
        });
        return bermudaTriangle;
    }

}

function initMap() {

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 5,
        center: { lat: 66.886, lng: 14.268 },
        mapTypeId: "terrain",
    });

    // const map = new google.maps.Map(document.getElementById("map"), {
    //     zoom: 30,
    //     center: { lat: 0, lng: 0 },
    //     mapTypeControl: true,
    // });

    // initGallPeters();
    // map.mapTypes.set("gallPeters", gallPetersMapType);
    // map.setMapTypeId("gallPeters");

    let hexes = jsonFile.data;
    let width = 0.25;
    let distortion = 3.0;
    for (let x = 0; x < 46; x+= distortion) {
        for (let y = 0; y < 7; y++)
        {
            let delta_x = 3 * width / 2 * x;
            let delta_y = 2* width * y;
            if((x/distortion) % 2 !== 0) {
                delta_y += width;
            }
            let hex = new Hex(17.0 + delta_x, 70.0 - delta_y);
            googleHex = hex.draw();
            googleHex.setMap(map);
            // Add a listener for the click event.
            googleHex.set("hex", hexes[0]);
            googleHex.addListener("click", showArrays);  
        }
    }

  
    infoWindow = new google.maps.InfoWindow();
}


let gallPetersMapType;

function initGallPeters() {
  const GALL_PETERS_RANGE_X = 800;
  const GALL_PETERS_RANGE_Y = 512;

  // Fetch Gall-Peters tiles stored locally on our server.
  gallPetersMapType = new google.maps.ImageMapType({
    getTileUrl: function (coord, zoom) {
      const scale = 1 << zoom;
      // Wrap tiles horizontally.
      const x = ((coord.x % scale) + scale) % scale;
      // Don't wrap tiles vertically.
      const y = coord.y;

      if (y < 0 || y >= scale) return "";
      return (
        "https://developers.google.com/maps/documentation/" +
        "javascript/examples/full/images/gall-peters_" +
        zoom +
        "_" +
        x +
        "_" +
        y +
        ".png"
      );
    },
    tileSize: new google.maps.Size(GALL_PETERS_RANGE_X, GALL_PETERS_RANGE_Y),
    minZoom: 0,
    maxZoom: 2,
    name: "Gall-Peters",
  });
  // Describe the Gall-Peters projection used by these tiles.
  gallPetersMapType.projection = {
    fromLatLngToPoint: function (latLng) {
      const latRadians = (latLng.lat() * Math.PI) / 180;
      return new google.maps.Point(
        GALL_PETERS_RANGE_X * (0.5 + latLng.lng() / 360),
        GALL_PETERS_RANGE_Y * (0.5 - 0.5 * Math.sin(latRadians))
      );
    },
    fromPointToLatLng: function (point, noWrap) {
      const x = point.x / GALL_PETERS_RANGE_X;
      const y = Math.max(0, Math.min(1, point.y / GALL_PETERS_RANGE_Y));
      return new google.maps.LatLng(
        (Math.asin(1 - 2 * y) * 180) / Math.PI,
        -180 + 360 * x,
        noWrap
      );
    },
  };
}

function createPrintout(atribute, atributeName) {
    return "<br>" + atributeName + ": " + atribute.max + ", " +  atribute.min;
}


function showArrays(event) {
  // Since this polygon has only one path, we can call getPath() to return the
  // MVCArray of LatLngs.
  const polygon = this;
  const vertices = polygon.getPath();

  let contentString =
    "<b>Hex</b><br>" +
    "Clicked location: <br>" +
    event.latLng.lat() +
    "," +
    event.latLng.lng() +
    "<br>";

    mhex = this.get("hex");

  contentString += createPrintout(mhex.temp, "Average year temperature");
  contentString += createPrintout(mhex.speed, "Average year wind speed");
  contentString += '<br><img src="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/google/110/heavy-check-mark_2714.png" alt="Italian Trulli">'

  // Replace the info window's content and position.
  infoWindow.setContent(contentString);
  infoWindow.setPosition(event.latLng);
  infoWindow.open(map);
}
