import { Box, HStack, Text } from '@chakra-ui/react';
import PropTypes from 'prop-types';
import { colorStops, noDataColor } from '../lib/colorScale';
import { metricCeilings, metricLabel } from '../lib/nutritionData';

const MapLegend = ({ indicator, mapMode }) => {
  const maximum = metricCeilings[indicator] || 55;

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
};

export default MapLegend;
