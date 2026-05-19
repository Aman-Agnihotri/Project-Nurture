import { Box, Container, Flex } from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';
import {
  aggregateRows,
  buildClusterRows,
  buildClusterLookup,
  defaultFilters,
  getClusterSegments,
  getFilterOptions,
  getFilteredSegments,
} from '../lib/nutritionData';
import MapComponent from './MapComponent';
import ModelComponent from './ModelComponent';

const baseUrl = import.meta.env.BASE_URL || '/';
const dhsDataUrl = `${baseUrl}generated/dhs_cluster_nutrition.json`;

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [status, setStatus] = useState('loading');
  const [filters, setFilters] = useState(defaultFilters);

  useEffect(() => {
    fetch(dhsDataUrl, { cache: 'no-store' })
      .then(response => {
        if (!response.ok) {
          throw new Error('DHS extract missing');
        }
        return response.json();
      })
      .then(data => {
        setDashboardData(data);
        setStatus('ready');
      })
      .catch(() => {
        setStatus('missing');
      });
  }, []);

  const updateFilter = (name, value) => {
    setFilters(current => ({
      ...current,
      [name]: value,
      ...(name === 'state' ? { district: 'All' } : {}),
    }));
  };

  const clusterLookup = useMemo(
    () => buildClusterLookup(dashboardData),
    [dashboardData],
  );

  const clusterSegments = useMemo(
    () => getClusterSegments(dashboardData, clusterLookup),
    [dashboardData, clusterLookup],
  );

  const filterOptions = useMemo(
    () => getFilterOptions(dashboardData, filters),
    [dashboardData, filters],
  );

  const filteredSegments = useMemo(
    () => getFilteredSegments(clusterSegments, filters),
    [clusterSegments, filters],
  );

  const filteredSummary = useMemo(
    () => aggregateRows(filteredSegments),
    [filteredSegments],
  );

  const filteredClusters = useMemo(
    () => buildClusterRows(filteredSegments),
    [filteredSegments],
  );

  return (
    <Container maxW="container.2xl" px={['4', '6', '8']} py="20" minH="100vh">
      <Flex direction={['column', 'column', 'row']} gap="6" alignItems="stretch">
        <Box flex="1.75" minW="0">
          <MapComponent
            clusters={filteredClusters}
            indicator={filters.indicator}
            mapMode={filters.mapMode}
            onMapModeChange={value => updateFilter('mapMode', value)}
            status={status}
          />
        </Box>
        <Box flex="1" minW={['full', 'full', '390px']}>
          <ModelComponent
            dashboardData={dashboardData}
            filterOptions={filterOptions}
            filteredClusters={filteredClusters}
            filters={filters}
            status={status}
            summary={filteredSummary}
            onFilterChange={updateFilter}
          />
        </Box>
      </Flex>
    </Container>
  );
};

export default Dashboard;
