// ---- Map ----
let map;
let markerCluster;

function initMap() {
  map = L.map('map').setView([20, 0], 3);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(map);
  markerCluster = L.markerClusterGroup({ maxClusterRadius: 50 });
  map.addLayer(markerCluster);
}

function getMapBbox() {
  const bounds = map.getBounds();
  return {
    lamin: bounds.getSouth().toFixed(4),
    lamax: bounds.getNorth().toFixed(4),
    lomin: bounds.getWest().toFixed(4),
    lomax: bounds.getEast().toFixed(4)
  };
}

function planeIcon(heading) {
  heading = heading || 0;
  return L.divIcon({
    html: `<div style="transform:rotate(${heading}deg);font-size:20px;line-height:1">✈</div>`,
    className: '',
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });
}

function loadMapFlights() {
  const bbox = getMapBbox();
  const status = document.getElementById('map-status');
  status.textContent = '⏳ Fetching flights…';
  const url = `/api/flights?lamin=${bbox.lamin}&lamax=${bbox.lamax}&lomin=${bbox.lomin}&lomax=${bbox.lomax}`;
  fetch(url)
    .then(r => r.json())
    .then(data => {
      markerCluster.clearLayers();
      const flights = data.flights || [];
      flights.forEach(f => {
        if (f.lat == null || f.lon == null) return;
        const marker = L.marker([f.lat, f.lon], { icon: planeIcon(f.heading) });
        marker.bindPopup(`
          <div class="flight-popup">
            <strong>${f.callsign || f.icao24}</strong>
            Country: ${f.origin_country || 'N/A'}<br>
            Altitude: ${f.altitude != null ? f.altitude + ' m' : 'N/A'}<br>
            Speed: ${f.velocity != null ? f.velocity + ' m/s' : 'N/A'}<br>
            Heading: ${f.heading != null ? f.heading + '°' : 'N/A'}<br>
            ICAO24: ${f.icao24}
          </div>
        `);
        markerCluster.addLayer(marker);
      });
      status.textContent = `✅ ${flights.length} flights loaded`;
    })
    .catch(() => { status.textContent = '❌ Failed to load flights'; });
}

// ---- Route Search ----
function searchRoutes() {
  const origin = document.getElementById('searchOrigin').value;
  const dest = document.getElementById('searchDest').value;
  const maxStops = document.getElementById('maxStops').value;
  const maxPrice = document.getElementById('maxPrice').value;
  let url = '/api/search?';
  if (origin) url += `origin=${encodeURIComponent(origin)}&`;
  if (dest) url += `destination=${encodeURIComponent(dest)}&`;
  if (maxStops) url += `max_stops=${maxStops}&`;
  if (maxPrice) url += `max_price=${maxPrice}&`;
  showLoading(true);
  fetch(url)
    .then(r => r.json())
    .then(data => { showLoading(false); displayRoutes(data.results || []); })
    .catch(() => showLoading(false));
}

function loadAllRoutes() {
  showLoading(true);
  fetch('/api/routes')
    .then(r => r.json())
    .then(data => { showLoading(false); displayRoutes(data.routes || []); })
    .catch(() => showLoading(false));
}

function showLoading(show) {
  document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function displayRoutes(routes) {
  const container = document.getElementById('routes');
  if (!routes.length) {
    container.innerHTML = '<p style="text-align:center;color:#888;padding:1em">No routes found.</p>';
    return;
  }
  container.innerHTML = routes.map(r => `
    <div class="route-card ${r.is_priority ? 'priority' : ''}">
      <div class="route-header">
        <div class="route-path">${r.origin} → ${r.destination}</div>
        ${r.is_priority ? '<span class="priority-badge">PRIORITY</span>' : ''}
      </div>
      <div class="route-details">
        <div class="detail-item">
          <span class="detail-label">Duration</span>
          <span class="detail-value">${r.duration_hours}h</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Stops</span>
          <span class="detail-value">${r.num_stops}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Price</span>
          <span class="detail-value price-value">
            $${(r.base_price || r.estimated_price || '?')}
            <span class="badge ${r.is_live ? 'badge-live' : 'badge-est'}">${r.is_live ? 'LIVE' : 'EST'}</span>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Airlines</span>
          <span class="detail-value">${(r.airlines || []).join(', ')}</span>
        </div>
      </div>
      ${r.stoppages && r.stoppages.length
        ? `<div class="stops-info">Via: ${r.stoppages.join(', ')}</div>`
        : '<div class="stops-info">Direct Flight</div>'}
    </div>
  `).join('');
}

// ---- AI Assistant ----
function ask() {
  const question = document.getElementById('question').value.trim();
  if (!question) return;
  document.getElementById('answer').textContent = '⏳ Thinking…';
  fetch('/api/aviation/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question})
  })
  .then(r => r.json())
  .then(data => {
    document.getElementById('answer').textContent = data.answer || data.error || 'No response';
  })
  .catch(() => {
    document.getElementById('answer').textContent = '❌ Request failed';
  });
}

// Allow Enter key in AI input
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('question').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') ask();
  });
  initMap();
  loadAllRoutes();
});
