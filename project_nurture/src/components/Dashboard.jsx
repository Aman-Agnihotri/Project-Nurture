import { Box, Container, Flex, HStack } from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';
import {
  aggregateRows,
  buildClusterRows,
  buildClusterLookup,
  buildPriorityAreas,
  defaultFilters,
  getClusterSegments,
  getFilterOptions,
  getFilteredSegments,
} from '../lib/nutritionData';
import DashboardGuide from './DashboardGuide';
import DashboardStatePanel from './DashboardStatePanel';
import DashboardTour from './DashboardTour';
import MapComponent from './MapComponent';
import ModelComponent from './ModelComponent';

const baseUrl = import.meta.env.BASE_URL || '/';
const dhsDataUrl = `${baseUrl}generated/dhs_cluster_nutrition.json`;
const filtersStorageKey = 'project-nurture-dashboard-filters';

const readStoredFilters = () => {
  if (typeof window === 'undefined') return defaultFilters;

  try {
    const stored = window.localStorage.getItem(filtersStorageKey);
    if (!stored) return defaultFilters;

    const parsed = JSON.parse(stored);
    return {
      ...defaultFilters,
      ...parsed,
    };
  } catch {
    return defaultFilters;
  }
};

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [status, setStatus] = useState('loading');
  const [filters, setFilters] = useState(readStoredFilters);

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

  useEffect(() => {
    window.localStorage.setItem(filtersStorageKey, JSON.stringify(filters));
  }, [filters]);

  const updateFilter = (name, value) => {
    setFilters(current => ({
      ...current,
      [name]: value,
      ...(name === 'state' ? { district: 'All' } : {}),
    }));
  };

  const resetFilters = () => {
    setFilters(defaultFilters);
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

  const priorityAreas = useMemo(
    () => buildPriorityAreas(filteredSegments, filters, filters.indicator),
    [filteredSegments, filters],
  );

  const hasGeneratedRows = clusterSegments.length > 0 && Boolean(dashboardData?.clusters?.length);
  const dashboardState = status === 'ready' && !hasGeneratedRows ? 'empty' : status;

  if (dashboardState !== 'ready') {
    return (
      <Container maxW="container.2xl" px={['4', '6', '8']} py={['8', '12', '20']} minH="100vh">
        <DashboardGuide />
        <DashboardStatePanel status={dashboardState} />
      </Container>
    );
  }

  return (
    <Container maxW="container.2xl" px={['4', '6', '8']} py={['8', '12', '20']} minH="100vh">
      <HStack justifyContent={['flex-start', 'flex-end']} mb="4">
        <DashboardTour />
      </HStack>
      <DashboardGuide />
      <Flex direction={['column', 'column', 'row']} gap="6" alignItems="stretch">
        <Box
          alignSelf={['stretch', 'stretch', 'flex-start']}
          flex="1.75"
          minW="0"
          position={['static', 'static', 'sticky']}
          top="20"
          data-tour="dashboard-map"
        >
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
            priorityAreas={priorityAreas}
            status={status}
            summary={filteredSummary}
            onFilterChange={updateFilter}
            onResetFilters={resetFilters}
          />
        </Box>
      </Flex>
    </Container>
  );
};

export default Dashboard;
