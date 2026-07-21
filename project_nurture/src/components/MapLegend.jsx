import { Box, HStack, Text } from '@chakra-ui/react';
import PropTypes from 'prop-types';
import { colorStops, noDataColor } from '../lib/colorScale';
import { metricCeilings, metricLabel } from '../lib/nutritionData';
import { TYPOLOGY_METRIC_KEY } from '../lib/typologies';

const MapLegend = ({ indicator, mapMode, typologyLegend, typologyPlaceholderStatus }) => {
  const maximum = metricCeilings[indicator] || 55;

  if (mapMode === 'choropleth' && indicator === TYPOLOGY_METRIC_KEY) {
    return (
      <Box className="map-legend" aria-label="Typology map legend">
        <Text fontSize="xs" fontWeight="bold">Demo district typology</Text>
        {typologyLegend.map(row => (
          <HStack key={row.id} fontSize="xs" align="start">
            <Box w="10px" h="10px" mt="3px" flexShrink="0" bg={row.color} />
            <span>{row.label}</span>
          </HStack>
        ))}
        <HStack fontSize="xs" color="app.muted">
          <Box w="10px" h="10px" flexShrink="0" bg={noDataColor} />
          <span>No district data</span>
        </HStack>
        <Text fontSize="xs" color="app.muted" mt="1">
          {typologyPlaceholderStatus || 'Placeholder demo patterns, not NFHS findings.'}
        </Text>
      </Box>
    );
  }

  return (
    <Box className="map-legend" aria-label={`${metricLabel(indicator)} map legend`}>
      <Text fontSize="xs" fontWeight="bold">{metricLabel(indicator)}</Text>
      <Box h="8px" borderRadius="full" bg={`linear-gradient(90deg, ${colorStops.join(', ')})`} />
      <HStack justify="space-between" fontSize="xs" color="app.muted">
        <span>0%</span><span>{maximum}%+</span>
      </HStack>
      {mapMode === 'choropleth' ? <HStack fontSize="xs" color="app.muted"><Box w="10px" h="10px" borderRadius="full" bg={noDataColor} /><span>No district data</span></HStack> : <Text fontSize="xs" color="app.muted">Colors show mapped cluster values</Text>}
    </Box>
  );
};

MapLegend.propTypes = {
  indicator: PropTypes.string.isRequired,
  mapMode: PropTypes.string.isRequired,
  typologyLegend: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  })),
  typologyPlaceholderStatus: PropTypes.string,
};

MapLegend.defaultProps = {
  typologyLegend: [],
  typologyPlaceholderStatus: '',
};

export default MapLegend;
