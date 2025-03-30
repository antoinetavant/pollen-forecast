const map = L.map('map').setView([46.8, 2.5], 5);
var geojson

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);


var info = L.control();

info.onAdd = function (map) {
    this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
    this.update();
    return this._div;
};

// method that we will use to update the control based on feature properties passed
info.update = function (props) {
    this._div.innerHTML = '<h4>Pollen Density</h4>' +  (props ?
      '<b>' + props.name + '</b><br />' + props.pollen_concentration.toFixed(2) + ' grains / m<sup>3</sup>'
      : 'Survole un departement');
};

info.addTo(map);

var legend = L.control({position: 'bottomright'});

legend.onAdd = function (map) {

    var div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 10, 50, 100, 250],
        labels = ["faible", "moderé", "modéré-fort", "fort", "très fort"];
        colors = ["#29ff08", "#FD8D3C", "#FC4E2A", "#BD0026", "#800026"]

    // loop through our density intervals and generate a label with a colored square for each interval
    for (var i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + colors[i] + '"></i> ' + labels[i] + ' '+
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + " gains/m<sup>3<\sup> " + '<br>' :  '+' + " gains/m<sup>3<\sup> ");
    }

    return div;
};

legend.addTo(map);

function styleFeature(feature) {
  return {
    fillColor: feature.properties.color,
    weight: 1,
    opacity: 1,
    color: 'white',
    fillOpacity: 0.7
  };
}

function highlightFeature(e) {
    var layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    layer.bringToFront();
    info.update(layer.feature.properties);
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}
function onEachFeature(feature, layer) {
    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        // click: zoomToFeature
    });
}


async function loadData() {
  console.log("lets go")
  const date = document.getElementById('date').value;
  const polenType = document.getElementById('polen_type').value;
  const spinner = document.getElementById('loading-spinner');
  spinner.classList.remove('d-none'); // Show the spinner

  try {
      const response = await fetch(`/api/departements-geojson/?date=${date}&pollen_type=${polenType}`);
      const data = await response.json();
      spinner.classList.add('d-none'); // Hide the spinner

      if (data.error) {
          alert(data.error);
          return;
      }

  //   console.log("Chart Data for Chart.js:", data); // Debug the data passed to Chart.js
  geojson = L.geoJson(data, {style: styleFeature,
    onEachFeature: onEachFeature}).addTo(map);
  } catch (error) {
        spinner.classList.add('d-none'); // Hide spinner
        console.error('Error fetching data for Leaflet.js:', error);
        alert('An error occurred while fetching data.');
    }
}
