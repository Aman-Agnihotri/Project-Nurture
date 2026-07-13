import { metricCeilings } from './nutritionData';

export const noDataColor = '#7a8794';
export const colorStops = ['#277da1', '#2f9e7e', '#f0a202', '#e5532d', '#b42318'];

export const colorFor = (value, metricKey) => {
  const score = Number(value);
  if (!Number.isFinite(score)) return noDataColor;

  const ceiling = metricCeilings[metricKey] || 55;
  const ratio = Math.max(0, Math.min(1, score / ceiling));
  return colorStops[Math.min(colorStops.length - 1, Math.floor(ratio * colorStops.length))];
};
