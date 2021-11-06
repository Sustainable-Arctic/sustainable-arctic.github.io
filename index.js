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

var jsonBuildings = {
    "parameters": [
        {
            "temp":
            {
                "min": -200,
                "max": 1000,
                "mean": 500
            },
            "speed":
            {
                "min": -300,
                "max": 2000,
                "mean": 800
            }   
        }, 
        {
            "temp":
            {
                "min": -200,
                "max": 1000,
                "mean": 500
            },
            "speed":
            {
                "min": -300,
                "max": 2000,
                "mean": 800
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
            strokeColor: "#111111",
            strokeOpacity: 0.8,
            strokeWeight: 3,
            fillColor: "#111111",
            fillOpacity: 0.35,
        });
        return bermudaTriangle;
    }

}

var googleHexes = [];

function calculateDistances()
{
    var e = document.getElementById("useCaseSelector");
    console.log("Selected use case" + e.value);



    let distances = [];
    for (let i = 0; i < googleHexes.length; i++) {

    }

}

function redrawMap()
{
    var e = document.getElementById("useCaseSelector");
    console.log("Selected use case" + e.value);

    for (let i = 0; i < googleHexes.length; i++) {
        googleHexes[i].setOptions({fillColor : 'red'});
    }
}

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 6,
        center: { lat: 69 - 0.420, lng: 26 },
        mapTypeId: "terrain",
        gestureHandling: "none",
        zoomControl: false,      
    });

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
            googleHex.set("hex", hexes[0]);
            googleHex.addListener("click", showArrays);  
            googleHexes.push(googleHex);
        }
    }

    infoWindow = new google.maps.InfoWindow();
}

function createPrintout(atribute, atributeName) {
    return "<br>" + atributeName + ": " + atribute.max + ", " +  atribute.min;
}

function showArrays(event) {
  const polygon = this;

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

  infoWindow.setContent(contentString);
  infoWindow.setPosition(event.latLng);
  infoWindow.open(map);
}
