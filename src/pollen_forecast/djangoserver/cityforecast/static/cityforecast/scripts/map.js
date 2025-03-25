const map = L.map('map').setView([46.8, 2.5], 5);


L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

  // Color scale for pollen concentration
  function getColor(d) {
    return d > 200 ? '#800026' :
           d > 150 ? '#BD0026' :
           d > 100 ? '#E31A1C' :
           d > 50  ? '#FC4E2A' :
           d > 20  ? '#FD8D3C' :
           d > 0   ? '#FEB24C' :
                     '#FFEDA0';
  }

  function styleFeature(feature, pollenValue) {
    return {
      fillColor: getColor(pollenValue),
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  }

  function updateMap(timeIndex) {
    const timeEntry = pollenForecastData.data[timeIndex];
    document.getElementById('currentTimeLabel').innerText = "Forecast: " + timeEntry.time;

    if (geojsonLayer) {
      map.removeLayer(geojsonLayer);
    }

    geojsonLayer = L.geoJson(departementsGeoJSON, {
      style: function (feature) {
        const deptCode = feature.properties.code;
        const pollenValue = timeEntry.departements[deptCode] || 0;
        return styleFeature(feature, pollenValue);
      },
      onEachFeature: function (feature, layer) {
        const deptCode = feature.properties.code;
        const deptName = feature.properties.nom;
        const pollenValue = timeEntry.departements[deptCode] || 0;
        layer.bindPopup(`<strong>${deptName}</strong><br>Pollen: ${pollenValue}`);
      }
    }).addTo(map);
  }

  function initSlider() {
    const slider = document.getElementById('timeSlider');
    slider.max = pollenForecastData.data.length - 1;
    slider.addEventListener('input', function() {
      updateMap(this.value);
    });
    updateMap(0);
  }

  async function loadData() {
  }
