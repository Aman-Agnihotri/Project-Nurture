export const metricOptions = [
  { key: 'risk_score', label: 'Composite risk' },
  { key: 'stunting_rate', label: 'Stunting' },
  { key: 'underweight_rate', label: 'Underweight' },
  { key: 'wasting_rate', label: 'Wasting' },
  { key: 'severe_wasting_rate', label: 'Severe wasting' },
  { key: 'overweight_rate', label: 'Overweight' },
  { key: 'anemia_rate', label: 'Anemia' },
];

export const mapModeOptions = [
  { key: 'clusters', label: 'Cluster risk' },
  { key: 'heat', label: 'Hotspot heat' },
  { key: 'both', label: 'Cluster + heat' },
];

export const metricCeilings = {
  risk_score: 55,
  stunting_rate: 55,
  underweight_rate: 55,
  wasting_rate: 35,
  severe_wasting_rate: 15,
  overweight_rate: 15,
  anemia_rate: 90,
};

export const defaultFilters = {
  indicator: 'risk_score',
  mapMode: 'clusters',
  state: 'All',
  district: 'All',
  residence: 'All',
  sex: 'All',
  wealth: 'All',
  ageBand: 'All',
};

const emptyFilterOptions = {
  states: [],
  districts: [],
  residences: [],
  sexes: [],
  wealth: [],
  ageBands: [],
};

export const sumFields = [
  'child_count',
  'haz_valid_n',
  'waz_valid_n',
  'whz_valid_n',
  'anemia_valid_n',
  'haz_den_w',
  'waz_den_w',
  'whz_den_w',
  'anemia_den_w',
  'stunted_w',
  'severely_stunted_w',
  'underweight_w',
  'severely_underweight_w',
  'wasted_w',
  'severely_wasted_w',
  'overweight_w',
  'anemia_w',
  'severe_anemia_w',
  'haz_z_w',
  'waz_z_w',
  'whz_z_w',
];

const uniqueSorted = values =>
  [...new Set(values.filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b)));

export const buildClusterLookup = dashboardData =>
  new Map((dashboardData?.clusters || []).map(cluster => [Number(cluster.cluster_id), cluster]));

export const getClusterSegments = (dashboardData, clusterLookup = buildClusterLookup(dashboardData)) => {
  const segments = dashboardData?.cluster_segments || [];
  const columns = dashboardData?.cluster_segment_columns || [];

  if (!segments.length) return [];
  if (!Array.isArray(segments[0])) {
    return segments;
  }
  if (!columns.length) return [];

  return segments
    .map(values => {
      const row = Object.fromEntries(columns.map((column, index) => [column, values[index]]));
      const cluster = clusterLookup.get(Number(row.cluster_id));

      if (!cluster) return null;

      return {
        ...row,
        dhs_id: cluster.dhs_id,
        state_code_gps: cluster.state_code_gps,
        state_name: cluster.state_name,
        district_name: cluster.district_name,
        urban_rural_gps: cluster.urban_rural_gps,
        latitude: cluster.latitude,
        longitude: cluster.longitude,
      };
    })
    .filter(Boolean);
};

export const metricLabel = key => metricOptions.find(metric => metric.key === key)?.label || key;

export const formatPercent = value => {
  const number = Number(value);
  return Number.isFinite(number) ? `${number.toFixed(1)}%` : 'No data';
};

export const formatCount = value => {
  const number = Number(value);
  return Number.isFinite(number) ? Math.round(number).toLocaleString('en-IN') : '0';
};

export const matchesFilters = (row, filters) => {
  if (filters.state !== 'All' && row.state_name !== filters.state) return false;
  if (filters.district !== 'All' && row.district_name !== filters.district) return false;
  if (filters.residence !== 'All' && row.urban_rural_gps !== filters.residence) return false;
  if (filters.sex !== 'All' && row.sex !== filters.sex) return false;
  if (filters.wealth !== 'All' && row.wealth !== filters.wealth) return false;
  if (filters.ageBand !== 'All' && row.age_band !== filters.ageBand) return false;
  return true;
};

const weightedRate = (numerator, denominator) =>
  denominator > 0 ? (100 * numerator) / denominator : null;

const weightedMeanZ = (numerator, denominator) =>
  denominator > 0 ? numerator / denominator / 100 : null;

export const addDerivedIndicators = aggregate => {
  const summary = { ...aggregate };

  summary.stunting_rate = weightedRate(summary.stunted_w, summary.haz_den_w);
  summary.severe_stunting_rate = weightedRate(summary.severely_stunted_w, summary.haz_den_w);
  summary.underweight_rate = weightedRate(summary.underweight_w, summary.waz_den_w);
  summary.severe_underweight_rate = weightedRate(
    summary.severely_underweight_w,
    summary.waz_den_w,
  );
  summary.wasting_rate = weightedRate(summary.wasted_w, summary.whz_den_w);
  summary.severe_wasting_rate = weightedRate(summary.severely_wasted_w, summary.whz_den_w);
  summary.overweight_rate = weightedRate(summary.overweight_w, summary.whz_den_w);
  summary.anemia_rate = weightedRate(summary.anemia_w, summary.anemia_den_w);
  summary.severe_anemia_rate = weightedRate(summary.severe_anemia_w, summary.anemia_den_w);

  summary.mean_haz = weightedMeanZ(summary.haz_z_w, summary.haz_den_w);
  summary.mean_waz = weightedMeanZ(summary.waz_z_w, summary.waz_den_w);
  summary.mean_whz = weightedMeanZ(summary.whz_z_w, summary.whz_den_w);

  const coreRates = [summary.stunting_rate, summary.underweight_rate, summary.wasting_rate];
  summary.risk_score = coreRates.every(Number.isFinite)
    ? summary.stunting_rate * 0.45 + summary.underweight_rate * 0.35 + summary.wasting_rate * 0.2
    : null;

  return summary;
};

export const aggregateRows = rows => {
  const aggregate = Object.fromEntries(sumFields.map(field => [field, 0]));

  rows.forEach(row => {
    sumFields.forEach(field => {
      aggregate[field] += Number(row[field]) || 0;
    });
  });

  return addDerivedIndicators(aggregate);
};

export const getFilteredSegments = (segments, filters) => {
  return segments.filter(row => matchesFilters(row, filters));
};

export const buildClusterRows = segments => {
  const byCluster = new Map();

  segments.forEach(segment => {
    const clusterId = segment.cluster_id;
    if (!byCluster.has(clusterId)) {
      byCluster.set(clusterId, {
        cluster_id: segment.cluster_id,
        dhs_id: segment.dhs_id,
        state_code_gps: segment.state_code_gps,
        state_name: segment.state_name,
        district_name: segment.district_name,
        urban_rural_gps: segment.urban_rural_gps,
        latitude: segment.latitude,
        longitude: segment.longitude,
        rows: [],
      });
    }

    byCluster.get(clusterId).rows.push(segment);
  });

  return [...byCluster.values()]
    .map(cluster => {
      const summary = aggregateRows(cluster.rows);
      const hazValid = Number(summary.haz_valid_n) || 0;
      const sampleQuality = hazValid >= 10 ? 'stable' : hazValid >= 5 ? 'limited' : 'sparse';

      return {
        ...cluster,
        ...summary,
        sample_quality: sampleQuality,
      };
    })
    .filter(cluster => Number.isFinite(Number(cluster.latitude)) && Number.isFinite(Number(cluster.longitude)));
};

const priorityGroupFor = filters => {
  if (filters.state === 'All') {
    return {
      key: 'state_name',
      scope: 'States / UTs',
      subtitleFor: row => `${formatCount(row.cluster_count)} mapped clusters`,
    };
  }

  if (filters.district === 'All') {
    return {
      key: 'district_name',
      scope: `Districts in ${filters.state}`,
      subtitleFor: row => `${row.state_name} · ${formatCount(row.cluster_count)} mapped clusters`,
    };
  }

  return {
    key: 'urban_rural_gps',
    scope: `Residence groups in ${filters.district}`,
    subtitleFor: row => `${row.district_name}, ${row.state_name}`,
  };
};

export const buildPriorityAreas = (segments, filters, indicator) => {
  const groupConfig = priorityGroupFor(filters);
  const byArea = new Map();

  segments.forEach(segment => {
    const label = segment[groupConfig.key] || 'Unspecified';

    if (!byArea.has(label)) {
      byArea.set(label, {
        label,
        state_name: segment.state_name,
        district_name: segment.district_name,
        clusterIds: new Set(),
        rows: [],
      });
    }

    const area = byArea.get(label);
    area.clusterIds.add(segment.cluster_id);
    area.rows.push(segment);
  });

  const rows = [...byArea.values()].map(area => {
    const summary = aggregateRows(area.rows);

    return {
      ...area,
      ...summary,
      cluster_count: area.clusterIds.size,
      clusterIds: undefined,
      rows: undefined,
    };
  });

  const maxChildren = Math.max(...rows.map(row => Number(row.child_count) || 0), 0);
  const maxLogChildren = Math.log10(maxChildren + 1) || 1;
  const ceiling = metricCeilings[indicator] || 55;

  const rankedRows = rows
    .map(row => {
      const metricValue = Number(row[indicator]);
      const childCount = Number(row.child_count) || 0;
      const severityIndex = Number.isFinite(metricValue)
        ? Math.min(100, Math.max(0, (metricValue / ceiling) * 100))
        : null;
      const sampleIndex = maxChildren > 0
        ? Math.min(100, (Math.log10(childCount + 1) / maxLogChildren) * 100)
        : 0;
      const priorityScore = severityIndex === null
        ? null
        : severityIndex * 0.75 + sampleIndex * 0.25;

      return {
        ...row,
        priority_score: priorityScore,
        priority_metric: metricValue,
        priority_subtitle: groupConfig.subtitleFor(row),
      };
    })
    .filter(row => Number.isFinite(row.priority_score))
    .sort((a, b) => b.priority_score - a.priority_score);

  return {
    scope: groupConfig.scope,
    rows: rankedRows,
  };
};

export const getFilterOptions = (dashboardData, filters) => {
  if (!dashboardData) return emptyFilterOptions;

  const clusters = dashboardData?.clusters || [];
  const dimensions = dashboardData.metadata?.filter_dimensions || {};
  const states = uniqueSorted(clusters.map(cluster => cluster.state_name));
  const districts = uniqueSorted(
    clusters
      .filter(cluster => filters.state === 'All' || cluster.state_name === filters.state)
      .map(cluster => cluster.district_name),
  );

  return {
    states,
    districts,
    residences: uniqueSorted(clusters.map(cluster => cluster.urban_rural_gps)),
    sexes: dimensions.sex || [],
    wealth: dimensions.wealth || [],
    ageBands: dimensions.age_band || [],
  };
};
