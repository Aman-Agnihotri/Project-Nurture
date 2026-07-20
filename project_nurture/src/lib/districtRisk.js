const finiteNumber = value => {
  const number = Number(value);
  return value !== null && value !== undefined && Number.isFinite(number) ? number : null;
};

const mean = values => {
  const finite = values.map(finiteNumber).filter(value => value !== null);
  return finite.length ? finite.reduce((total, value) => total + value, 0) / finite.length : null;
};

/** Overlay Phase 4 percentile risk on public district records only. */
export const applyDistrictRisk = (indicatorData, riskData) => {
  if (riskData?.schema_version !== '1.0' || !Array.isArray(riskData?.districts)) {
    throw new Error('District risk artifact must use schema_version 1.0');
  }

  const riskBySlug = new Map(riskData.districts.map(record => [record.district_slug, record]));
  const districts = (indicatorData?.districts || []).map(district => {
    const risk = riskBySlug.get(district.district_slug);
    const composite = finiteNumber(risk?.composite_score);
    return {
      ...district,
      risk_score: composite,
      stunting_percentile: finiteNumber(risk?.stunting_percentile),
      underweight_percentile: finiteNumber(risk?.underweight_percentile),
      wasting_percentile: finiteNumber(risk?.wasting_percentile),
    };
  });

  const states = (indicatorData?.states || []).map(state => ({
    ...state,
    risk_score: mean(
      districts
        .filter(district => district.state_slug === state.state_slug)
        .map(district => district.risk_score),
    ),
  }));

  return {
    ...indicatorData,
    metadata: {
      ...indicatorData?.metadata,
      risk_methodology: 'phase-4-district-percentile',
      risk_placeholder_status: riskData.metadata?.placeholder_status,
    },
    districts,
    states,
    national: {
      ...indicatorData?.national,
      risk_score: mean(districts.map(district => district.risk_score)),
    },
  };
};
