import { metricCeilings } from './nutritionData.js';

export const noDataColor = '#7a8794';
export const colorStops = ['#277da1', '#2f9e7e', '#f0a202', '#e5532d', '#b42318'];

export const colorFor = (value, metricKey) => {
  if (value === null || value === undefined || value === '') return noDataColor;

  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return noDataColor;

  const score = Math.max(0, Math.min(numericValue, metricCeilings[metricKey] || 100));
  if (metricKey === 'anemia_rate') {
    if (score >= 70) return colorStops[4];
    if (score >= 60) return colorStops[3];
    if (score >= 50) return colorStops[2];
    if (score >= 35) return colorStops[1];
    return colorStops[0];
  }
  if (metricKey === 'severe_wasting_rate' || metricKey === 'overweight_rate') {
    if (score >= 10) return colorStops[4];
    if (score >= 7) return colorStops[3];
    if (score >= 4) return colorStops[2];
    if (score >= 2) return colorStops[1];
    return colorStops[0];
  }
  if (score >= 45) return colorStops[4];
  if (score >= 35) return colorStops[3];
  if (score >= 25) return colorStops[2];
  if (score >= 15) return colorStops[1];
  return colorStops[0];
};
