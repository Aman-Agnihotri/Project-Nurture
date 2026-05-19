import { useEffect, useRef } from 'react';
import L from 'leaflet';
import PropTypes from 'prop-types';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.heat';
import { formatCount, formatPercent, metricLabel } from '../lib/nutritionData';

const escapeHtml = value =>
  String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

const metricMax = {
  risk_score: 55,
  stunting_rate: 55,
  underweight_rate: 55,
  wasting_rate: 35,
  severe_wasting_rate: 15,
  overweight_rate: 15,
  anemia_rate: 90,
};

const metricColor = (value, indicator, sampleQuality) => {
  if (sampleQuality === 'sparse') return '#7a8794';

  const score = Number(value);
  if (!Number.isFinite(score)) return '#7a8794';

  if (indicator === 'anemia_rate') {
    if (score >= 70) return '#b42318';
    if (score >= 60) return '#e5532d';
    if (score >= 50) return '#f0a202';
    if (score >= 35) return '#2f9e7e';
    return '#277da1';
  }

  if (indicator === 'severe_wasting_rate' || indicator === 'overweight_rate') {
    if (score >= 10) return '#b42318';
    if (score >= 7) return '#e5532d';
    if (score >= 4) return '#f0a202';
    if (score >= 2) return '#2f9e7e';
    return '#277da1';
  }

  if (score >= 45) return '#b42318';
  if (score >= 35) return '#e5532d';
  if (score >= 25) return '#f0a202';
  if (score >= 15) return '#2f9e7e';
  return '#277da1';
};

const createMetricIcon = (cluster, indicator) => {
  const color = metricColor(cluster[indicator], indicator, cluster.sample_quality);
  const size = cluster.sample_quality === 'stable' ? 20 : 16;

  return L.divIcon({
    className: 'risk-marker-shell',
    html: `<span class="risk-marker" style="--marker-color:${color}; width:${size}px; height:${size}px"></span>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
};

const dhsPopup = (cluster, indicator) => `
  <div class="nutrition-popup">
    <div class="popup-title">${escapeHtml(cluster.district_name || 'DHS cluster')}</div>
    <div class="popup-subtitle">
      ${escapeHtml(cluster.state_name)} · ${escapeHtml(cluster.urban_rural_gps)} · Cluster ${escapeHtml(cluster.cluster_id)}
    </div>
    <div class="popup-highlight">
      <span>${escapeHtml(metricLabel(indicator))}</span>
      <strong>${formatPercent(cluster[indicator])}</strong>
    </div>
    <div class="popup-grid">
      <span>Composite risk</span><strong>${formatPercent(cluster.risk_score)}</strong>
      <span>Stunted</span><strong>${formatPercent(cluster.stunting_rate)}</strong>
      <span>Underweight</span><strong>${formatPercent(cluster.underweight_rate)}</strong>
      <span>Wasted</span><strong>${formatPercent(cluster.wasting_rate)}</strong>
      <span>Anemia</span><strong>${formatPercent(cluster.anemia_rate)}</strong>
      <span>Children</span><strong>${formatCount(cluster.child_count)}</strong>
    </div>
    <div class="popup-note">${escapeHtml(cluster.sample_quality)} sample · displaced DHS GPS point</div>
  </div>
`;

const addLegend = (map, indicator) => {
  const legend = L.control({ position: 'bottomright' });
  const isAnemia = indicator === 'anemia_rate';
  const isLowRange = indicator === 'severe_wasting_rate' || indicator === 'overweight_rate';

  const labels = isAnemia
    ? ['70%+', '60-70%', '50-60%', '35-50%', '<35%']
    : isLowRange
      ? ['10%+', '7-10%', '4-7%', '2-4%', '<2%']
      : ['45%+', '35-45%', '25-35%', '15-25%', '<15%'];

  legend.onAdd = () => {
    const div = L.DomUtil.create('div', 'nutrition-legend');
    div.innerHTML = `
      <strong>${escapeHtml(metricLabel(indicator))}</strong>
      <span><i style="background:#b42318"></i>${labels[0]}</span>
      <span><i style="background:#e5532d"></i>${labels[1]}</span>
      <span><i style="background:#f0a202"></i>${labels[2]}</span>
      <span><i style="background:#2f9e7e"></i>${labels[3]}</span>
      <span><i style="background:#277da1"></i>${labels[4]}</span>
      <span><i style="background:#7a8794"></i>sparse sample</span>
    `;
    return div;
  };

  legend.addTo(map);
  return legend;
};

const mapMessageFor = (status, clusters) => {
  if (status === 'loading') return 'Loading India DHS dashboard extract...';
  if (status === 'missing') {
    return 'Run `python python_backend/dhs_pipeline.py` to generate the local India DHS dashboard extract.';
  }
  if (clusters.length === 0) return 'No DHS clusters match the selected filters.';
  return '';
};

const MapComponent = ({ clusters = [], indicator = 'risk_score', status = 'ready' }) => {
  const mapRef = useRef(null);
  const message = mapMessageFor(status, clusters);

  useEffect(() => {
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

    const heatPoints = [];
    const mapBounds = L.latLngBounds([]);

    clusters.forEach(cluster => {
      const lat = Number(cluster.latitude);
      const lon = Number(cluster.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      const marker = L.marker([lat, lon], {
        icon: createMetricIcon(cluster, indicator),
        title: `${cluster.district_name || 'DHS cluster'} ${formatPercent(cluster[indicator])}`,
      });
      marker.bindPopup(dhsPopup(cluster, indicator));
      markers.addLayer(marker);
      mapBounds.extend([lat, lon]);

      const metricValue = Number(cluster[indicator]);
      const maxValue = metricMax[indicator] || 55;
      if (Number.isFinite(metricValue)) {
        heatPoints.push([lat, lon, Math.max(0.15, Math.min(1, metricValue / maxValue))]);
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

    if (mapBounds.isValid()) {
      map.fitBounds(mapBounds.pad(0.08), { maxZoom: 6 });
    }

    legend = addLegend(map, indicator);

    return () => {
      if (heatLayer) heatLayer.remove();
      if (legend) legend.remove();
      map.remove();
    };
  }, [clusters, indicator]);

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

          .popup-highlight {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            margin-top: 12px;
            padding: 8px 10px;
            border-radius: 6px;
            background: #f3f6f8;
            font-size: 13px;
          }

          .popup-highlight strong {
            color: #172033;
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
        {message && <div className="map-message">{message}</div>}
        <div ref={mapRef} style={{ height: '100%', width: '100%' }} />
      </div>
    </>
  );
};

MapComponent.propTypes = {
  clusters: PropTypes.arrayOf(PropTypes.object),
  indicator: PropTypes.string,
  status: PropTypes.string,
};

export default MapComponent;
