import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.heat';

const baseUrl = import.meta.env.BASE_URL || '/';
const dhsDataUrl = `${baseUrl}generated/dhs_cluster_nutrition.json`;

const escapeHtml = value =>
  String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

const formatPercent = value => {
  const number = Number(value);
  return Number.isFinite(number) ? `${number.toFixed(1)}%` : 'No data';
};

const formatNumber = value => {
  const number = Number(value);
  return Number.isFinite(number) ? number.toLocaleString('en-IN') : '0';
};

const riskColor = (riskScore, sampleQuality) => {
  if (sampleQuality === 'sparse') return '#7a8794';

  const score = Number(riskScore);
  if (!Number.isFinite(score)) return '#7a8794';
  if (score >= 45) return '#b42318';
  if (score >= 35) return '#e5532d';
  if (score >= 25) return '#f0a202';
  if (score >= 15) return '#2f9e7e';
  return '#277da1';
};

const createRiskIcon = cluster => {
  const color = riskColor(cluster.risk_score, cluster.sample_quality);
  const size = cluster.sample_quality === 'stable' ? 20 : 16;

  return L.divIcon({
    className: 'risk-marker-shell',
    html: `<span class="risk-marker" style="--marker-color:${color}; width:${size}px; height:${size}px"></span>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
};

const dhsPopup = cluster => `
  <div class="nutrition-popup">
    <div class="popup-title">${escapeHtml(cluster.district_name || 'DHS cluster')}</div>
    <div class="popup-subtitle">
      ${escapeHtml(cluster.state_name)} · ${escapeHtml(cluster.urban_rural_gps)} · Cluster ${escapeHtml(cluster.cluster_id)}
    </div>
    <div class="popup-grid">
      <span>Risk score</span><strong>${formatPercent(cluster.risk_score)}</strong>
      <span>Stunted</span><strong>${formatPercent(cluster.stunting_rate)}</strong>
      <span>Underweight</span><strong>${formatPercent(cluster.underweight_rate)}</strong>
      <span>Wasted</span><strong>${formatPercent(cluster.wasting_rate)}</strong>
      <span>Anemia</span><strong>${formatPercent(cluster.anemia_rate)}</strong>
      <span>Children</span><strong>${formatNumber(cluster.child_count)}</strong>
    </div>
    <div class="popup-note">${escapeHtml(cluster.sample_quality)} sample · displaced DHS GPS point</div>
  </div>
`;

const fetchJson = async url => {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`Unable to load ${url}`);
  }
  return response.json();
};

const loadMapData = async () => {
  const dhsData = await fetchJson(dhsDataUrl);
  if (Array.isArray(dhsData.clusters) && dhsData.clusters.length > 0) {
    return dhsData;
  }

  throw new Error('DHS dashboard extract has no cluster records.');
};

const addLegend = map => {
  const legend = L.control({ position: 'bottomright' });

  legend.onAdd = () => {
    const div = L.DomUtil.create('div', 'nutrition-legend');
    div.innerHTML = `
          <strong>Nutrition Risk</strong>
          <span><i style="background:#b42318"></i>45%+</span>
          <span><i style="background:#e5532d"></i>35-45%</span>
          <span><i style="background:#f0a202"></i>25-35%</span>
          <span><i style="background:#2f9e7e"></i>15-25%</span>
          <span><i style="background:#277da1"></i>&lt;15%</span>
          <span><i style="background:#7a8794"></i>sparse sample</span>
        `;
    return div;
  };

  legend.addTo(map);
  return legend;
};

const MapComponent = () => {
  const mapRef = useRef(null);
  const [mapMessage, setMapMessage] = useState('');

  useEffect(() => {
    let disposed = false;
    let heatLayer = null;
    let legend = null;

    const tile = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18,
      minZoom: 3,
    });

    const map = L.map(mapRef.current, {
      center: [22.9734, 78.6569],
      zoom: 5,
      zoomSnap: 0.25,
      layers: [tile],
      preferCanvas: true,
    });

    const markers = L.markerClusterGroup({
      chunkedLoading: true,
      maxClusterRadius: 44,
      showCoverageOnHover: false,
      spiderfyDistanceMultiplier: 1.2,
    });

    loadMapData()
      .then(payload => {
        if (disposed) return;

        const heatPoints = [];

        payload.clusters.forEach(cluster => {
          const lat = Number(cluster.latitude);
          const lon = Number(cluster.longitude);
          if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

          const marker = L.marker([lat, lon], {
            icon: createRiskIcon(cluster),
            title: `${cluster.district_name || 'DHS cluster'} ${formatPercent(cluster.risk_score)}`,
          });
          marker.bindPopup(dhsPopup(cluster));
          markers.addLayer(marker);

          const risk = Number(cluster.risk_score);
          if (Number.isFinite(risk)) {
            heatPoints.push([lat, lon, Math.max(0.15, Math.min(1, risk / 55))]);
          }
        });

        markers.addTo(map);
        heatLayer = L.heatLayer(heatPoints, {
          radius: 24,
          blur: 18,
          maxZoom: 8,
          gradient: {
            0.1: '#277da1',
            0.3: '#2f9e7e',
            0.5: '#f0a202',
            0.7: '#e5532d',
            1: '#b42318',
          },
        }).addTo(map);

        if (markers.getLayers().length > 0) {
          map.fitBounds(markers.getBounds().pad(0.08), { maxZoom: 6 });
        }

        legend = addLegend(map);
      })
      .catch(error => {
        console.error(error);
        setMapMessage('Run `python python_backend/dhs_pipeline.py` to generate the local India DHS dashboard extract.');
      });

    return () => {
      disposed = true;
      if (heatLayer) heatLayer.remove();
      if (legend) legend.remove();
      map.remove();
    };
  }, []);

  return (
    <>
      <style>
        {`
          .map-container {
            position: relative;
            min-height: 640px;
            height: calc(100vh - 8rem);
            width: 100%;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 16px 36px rgba(15, 23, 42, 0.14);
            background: #e8eef2;
          }

          .risk-marker-shell {
            background: transparent;
            border: none;
          }

          .risk-marker {
            display: block;
            border-radius: 999px;
            background: var(--marker-color);
            border: 2px solid #ffffff;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.32);
          }

          .nutrition-popup {
            min-width: 230px;
            color: #172033;
          }

          .popup-title {
            font-weight: 800;
            font-size: 15px;
            line-height: 1.2;
          }

          .popup-subtitle,
          .popup-note {
            color: #637083;
            font-size: 12px;
            margin-top: 4px;
          }

          .popup-grid {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 7px 14px;
            margin-top: 12px;
            font-size: 13px;
          }

          .popup-grid span {
            color: #536176;
          }

          .popup-grid strong {
            color: #172033;
          }

          .nutrition-legend {
            display: grid;
            gap: 6px;
            padding: 10px 12px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.18);
            color: #172033;
            font-size: 12px;
          }

          .nutrition-legend strong {
            font-size: 13px;
          }

          .nutrition-legend span {
            display: flex;
            align-items: center;
            gap: 7px;
            white-space: nowrap;
          }

          .nutrition-legend i {
            width: 12px;
            height: 12px;
            display: inline-block;
            border-radius: 999px;
          }

          .map-message {
            position: absolute;
            z-index: 500;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            max-width: 420px;
            padding: 18px 20px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.96);
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
            color: #172033;
            font-size: 14px;
            line-height: 1.5;
            text-align: center;
          }
        `}
      </style>
      <div className="map-container">
        {mapMessage && <div className="map-message">{mapMessage}</div>}
        <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
      </div>
    </>
  );
};

export default MapComponent;
