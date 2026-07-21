import { noDataColor } from './colorScale.js';

export const TYPOLOGY_METRIC_KEY = 'typology';
export const typologyPalette = [
  '#0072B2',
  '#E69F00',
  '#009E73',
  '#CC79A7',
  '#56B4E9',
  '#D55E00',
];

const validatedTypologies = artifact => {
  if (
    artifact?.schema_version !== '1.0'
    || !Array.isArray(artifact?.districts)
    || !Array.isArray(artifact?.typologies)
  ) {
    throw new Error('District typology artifact must use schema_version 1.0');
  }
  return artifact.typologies;
};

export const typologyLegendData = artifact => validatedTypologies(artifact).map(
  (typology, index) => ({
    id: typology.id,
    label: typology.label,
    description: typology.description,
    color: typologyPalette[index % typologyPalette.length],
  }),
);

export const typologyColorFor = record => record?.typology_color || noDataColor;

/** Join committed typology assignments to public districts by stable slug. */
export const applyDistrictTypologies = (indicatorData, artifact) => {
  const legend = typologyLegendData(artifact);
  const typologyById = new Map(legend.map(row => [row.id, row]));
  const assignmentBySlug = new Map(
    artifact.districts.map(row => [row.district_slug, row.typology_id]),
  );
  const districts = (indicatorData?.districts || []).map(district => {
    const typologyId = assignmentBySlug.get(district.district_slug) || null;
    const typology = typologyById.get(typologyId);
    return {
      ...district,
      typology_id: typology?.id || null,
      typology_label: typology?.label || null,
      typology_description: typology?.description || null,
      typology_color: typology?.color || null,
    };
  });

  return {
    ...indicatorData,
    metadata: {
      ...indicatorData?.metadata,
      typology_placeholder_status: artifact.metadata?.placeholder_status,
    },
    districts,
    typologyLegend: legend,
  };
};
