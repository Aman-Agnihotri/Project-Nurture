import { Box, Text } from '@chakra-ui/react';
import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import PropTypes from 'prop-types';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.heat';
import { colorFor } from '../lib/colorScale';
import { TYPOLOGY_METRIC_KEY, typologyColorFor } from '../lib/typologies';
import {
  buildDistrictLookup,
  createGeometryLoader,
  districtForFeature,
} from '../lib/districtGeo';
import { cleanupLeafletLayers } from '../lib/mapLayers';
import { formatPercent, mapModeOptions, metricCeilings, metricLabel } from '../lib/nutritionData';
import MapLegend from './MapLegend';

const baseUrl = import.meta.env.BASE_URL || '/';
const escapeHtml = value => String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#039;');

const finiteMetricValue = value => {
  if (value === null || value === undefined || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
};

const metricIcon = (cluster, indicator) => {
  const value = cluster.sample_quality === 'sparse' ? null : cluster[indicator];
  const color = colorFor(value, indicator);
  return L.divIcon({
    className: 'risk-marker-shell',
    html: `<span class="risk-marker" style="--marker-color:${color}"></span>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });
};

const clusterIcon = (cluster, indicator) => {
  const markers = cluster.getAllChildMarkers();
  const totals = markers.reduce((result, marker) => {
    const value = finiteMetricValue(marker.options.metricValue);
    const childCount = Number(marker.options.childCount) || 0;
    const weight = childCount > 0 ? childCount : 1;
    if (value !== null) {
      result.weight += weight;
      result.weightedValue += value * weight;
    }
    return result;
  }, { weight: 0, weightedValue: 0 });
  const value = totals.weight > 0 ? totals.weightedValue / totals.weight : null;
  const color = colorFor(value, indicator);
  return L.divIcon({
    className: 'nutrition-cluster-icon',
    html: `<div class="nutrition-cluster-bubble" style="--cluster-color:${color}"><strong>${Number.isFinite(value) ? `${Math.round(value)}%` : 'N/A'}</strong><span>${markers.length} clusters</span></div>`,
    iconSize: [54, 54], iconAnchor: [27, 27],
  });
};

const MapComponent = ({ clusters, districts, indicator, mapMode, onMapModeChange, onDistrictNavigate, status, typologyLegend, typologyPlaceholderStatus }) => {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const geometryRef = useRef(null);
  const geometryLoaderRef = useRef(null);
  const [geometryStatus, setGeometryStatus] = useState('idle');

  if (!geometryLoaderRef.current) {
    geometryLoaderRef.current = createGeometryLoader(`${baseUrl}demo/geo/india_districts.geojson`);
  }

  useEffect(() => {
    const map = L.map(containerRef.current, { center: [22.9734, 78.6569], zoom: 5, zoomSnap: 0.25, preferCanvas: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 18, minZoom: 3,
    }).addTo(map);
    mapRef.current = map;
    return () => { map.remove(); mapRef.current = null; };
  }, []);

  useEffect(() => {
    if (mapMode !== 'choropleth' || geometryRef.current) return undefined;
    let active = true;
    setGeometryStatus('loading');
    geometryLoaderRef.current()
      .then(geometry => {
        if (active) { geometryRef.current = geometry; setGeometryStatus('ready'); }
      })
      .catch(() => { if (active) setGeometryStatus('missing'); });
    return () => { active = false; };
  }, [mapMode]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return undefined;
    const layers = [];
    const showClusters = mapMode === 'clusters' || mapMode === 'both';
    const showHeat = mapMode === 'heat' || mapMode === 'both';
    if (showClusters) {
      const markers = L.markerClusterGroup({ chunkedLoading: true, iconCreateFunction: group => clusterIcon(group, indicator), maxClusterRadius: 44, showCoverageOnHover: false });
      clusters.forEach(cluster => {
        const lat = Number(cluster.latitude); const lon = Number(cluster.longitude);
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
        const markerValue = cluster.sample_quality === 'sparse'
          ? null
          : finiteMetricValue(cluster[indicator]);
        const marker = L.marker([lat, lon], {
          childCount: Number(cluster.child_count) || 0,
          icon: metricIcon(cluster, indicator),
          metricValue: markerValue,
        });
        marker.bindPopup(`<strong>${escapeHtml(cluster.district_name || 'DHS cluster')}</strong><br>${escapeHtml(metricLabel(indicator))}: ${formatPercent(cluster[indicator])}`);
        markers.addLayer(marker);
      });
      markers.addTo(map); layers.push(markers);
    }
    if (showHeat) {
      const ceiling = metricCeilings[indicator] || 55;
      const points = clusters.map(row => {
        const value = finiteMetricValue(row[indicator]);
        return [Number(row.latitude), Number(row.longitude), value === null ? null : value / ceiling];
      }).filter(([lat, lon, value]) => Number.isFinite(lat) && Number.isFinite(lon) && value !== null);
      if (points.length) { const heat = L.heatLayer(points, { radius: 18, blur: 20, minOpacity: 0.18 }); heat.addTo(map); layers.push(heat); }
    }
    if (mapMode === 'choropleth' && geometryRef.current) {
      const byName = buildDistrictLookup(districts);
      const isTypology = indicator === TYPOLOGY_METRIC_KEY;
      const layer = L.geoJSON(geometryRef.current, {
        style: feature => {
          const record = districtForFeature(feature, byName);
          const hasValue = isTypology ? Boolean(record?.typology_id) : Boolean(record);
          return { color: '#ffffff', weight: 1, fillColor: isTypology ? typologyColorFor(record) : colorFor(record?.[indicator], indicator), fillOpacity: hasValue ? 0.72 : 0.48 };
        },
        onEachFeature: (feature, polygon) => {
          const props = feature.properties || {};
          const record = districtForFeature(feature, byName);
          const name = Reflect.get(props, 'district_name') || 'District';
          const tooltip = isTypology
            ? (record?.typology_label
              ? `${escapeHtml(name)}<br>Typology: ${escapeHtml(record.typology_label)}<br><em>Demo placeholder pattern</em>`
              : `${escapeHtml(name)}<br>No typology data`)
            : (record ? `${escapeHtml(name)}<br>${escapeHtml(metricLabel(indicator))}: ${formatPercent(record[indicator])}` : `${escapeHtml(name)}<br>No data`);
          polygon.bindTooltip(tooltip);
          polygon.on({ mouseover: () => polygon.setStyle({ weight: 3, fillOpacity: 0.9 }), mouseout: () => layer.resetStyle(polygon), click: () => { if (record) onDistrictNavigate(record); } });
        },
      }).addTo(map);
      layers.push(layer);
    }
    return () => cleanupLeafletLayers(layers);
  }, [clusters, districts, geometryStatus, indicator, mapMode, onDistrictNavigate]);

  const message = status === 'missing' ? 'Dashboard data is unavailable.' : (!clusters.length && mapMode !== 'choropleth' ? 'No DHS clusters match the selected filters.' : '');
  return <Box className="map-container">
    <Box className="map-layer-control" aria-label="Map layer">
      {mapModeOptions.map(mode => <button key={mode.key} className={mapMode === mode.key ? 'is-active' : ''} type="button" onClick={() => onMapModeChange(mode.key)}>{mode.label}</button>)}
    </Box>
    {(message || (mapMode === 'choropleth' && geometryStatus === 'missing')) && <Box className="map-message"><Text>{message || 'District boundaries have not been added yet. See public/demo/geo/README.md for the maintainer preparation step.'}</Text></Box>}
    <MapLegend indicator={indicator} mapMode={mapMode} typologyLegend={typologyLegend} typologyPlaceholderStatus={typologyPlaceholderStatus} />
    <Box ref={containerRef} h="100%" w="100%" />
    <style>{`.map-container{position:relative;min-height:640px;height:calc(100vh - 8rem);border-radius:8px;overflow:hidden;background:#e8eef2}.map-layer-control{position:absolute;z-index:650;top:14px;right:14px;display:flex;gap:4px;padding:4px;border-radius:8px;background:#fff;box-shadow:0 8px 22px #0002}.map-layer-control button{border:0;border-radius:5px;padding:7px 9px;background:transparent;font-size:12px;cursor:pointer}.map-layer-control .is-active{background:#0f766e;color:white}.map-legend{position:absolute;z-index:650;right:12px;bottom:30px;width:190px;padding:9px 11px;border-radius:8px;background:#fff;box-shadow:0 8px 22px #0002}.risk-marker-shell,.nutrition-cluster-icon{background:transparent;border:0}.risk-marker{display:block;width:20px;height:20px;border-radius:50%;background:var(--marker-color);border:2px solid white}.nutrition-cluster-bubble{width:54px;height:54px;display:flex;flex-direction:column;align-items:center;justify-content:center;border-radius:50%;background:var(--cluster-color);border:3px solid #fff;color:#111;font-size:11px;text-align:center}.nutrition-cluster-bubble strong{font-size:15px}.map-message{position:absolute;z-index:650;left:50%;top:50%;transform:translate(-50%,-50%);max-width:360px;padding:14px;border-radius:8px;background:#fff;text-align:center;box-shadow:0 8px 22px #0002}@media(max-width:768px){.map-container{min-height:430px;height:62vh}.map-layer-control{left:56px;right:8px;overflow:auto}.map-layer-control button{white-space:nowrap}.map-legend{bottom:28px;left:10px;right:auto;width:170px}}`}</style>
  </Box>;
};

MapComponent.propTypes = { clusters: PropTypes.arrayOf(PropTypes.object), districts: PropTypes.arrayOf(PropTypes.object), indicator: PropTypes.string, mapMode: PropTypes.string, onMapModeChange: PropTypes.func.isRequired, onDistrictNavigate: PropTypes.func.isRequired, status: PropTypes.string, typologyLegend: PropTypes.arrayOf(PropTypes.object), typologyPlaceholderStatus: PropTypes.string };
MapComponent.defaultProps = { clusters: [], districts: [], indicator: 'risk_score', mapMode: 'clusters', status: 'ready', typologyLegend: [], typologyPlaceholderStatus: '' };
export default MapComponent;
