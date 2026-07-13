import { Box, Container, Flex, HStack } from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  aggregateRows,
  buildAreaInsight,
  buildClusterRows,
  buildClusterLookup,
  buildPriorityAreas,
  defaultFilters,
  getClusterSegments,
  getFilterOptions,
  getFilteredSegments,
} from '../lib/nutritionData';
import { toSlug } from '../lib/slugs';
import { loadDashboardData, loadDistrictIndicators } from '../lib/dataSource';
import DashboardGuide from './DashboardGuide';
import DashboardStatePanel from './DashboardStatePanel';
import DashboardTour from './DashboardTour';
import DemoBanner from './DemoBanner';
import MapComponent from './MapComponent';
import ModelComponent from './ModelComponent';

const baseUrl = import.meta.env.BASE_URL || '/';
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
  const [tier, setTier] = useState(null);
  const [filters, setFilters] = useState(readStoredFilters);
  const [selectedPriorityAreaLabel, setSelectedPriorityAreaLabel] = useState(null);
  const [districtIndicators, setDistrictIndicators] = useState({ districts: [] });
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    loadDashboardData(baseUrl)
      .then(result => {
        setDashboardData(result.data);
        setTier(result.tier);
        setStatus('ready');
      })
      .catch(() => {
        setStatus('missing');
      });
  }, []);

  useEffect(() => {
    loadDistrictIndicators(baseUrl).then(setDistrictIndicators).catch(() => setDistrictIndicators({ districts: [] }));
  }, []);

  useEffect(() => {
    window.localStorage.setItem(filtersStorageKey, JSON.stringify(filters));
  }, [filters]);

  useEffect(() => {
    const requestedState = new URLSearchParams(location.search).get('state');
    const matchedState = (dashboardData?.clusters || []).map(row => row.state_name).find(name => toSlug(name) === requestedState);
    if (matchedState) setFilters(current => current.state === matchedState ? current : { ...current, state: matchedState, district: 'All' });
  }, [dashboardData, location.search]);

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

  useEffect(() => {
    setSelectedPriorityAreaLabel(current => {
      if (priorityAreas.rows.some(area => area.label === current)) {
        return current;
      }

      return priorityAreas.rows[0]?.label || null;
    });
  }, [priorityAreas]);

  const selectedPriorityArea = useMemo(
    () => priorityAreas.rows.find(area => area.label === selectedPriorityAreaLabel) || null,
    [priorityAreas, selectedPriorityAreaLabel],
  );

  const areaInsight = useMemo(
    () => buildAreaInsight(filteredSegments, filters, filters.indicator, selectedPriorityArea),
    [filteredSegments, filters, selectedPriorityArea],
  );

  const drillIntoArea = () => {
    if (!areaInsight) return;

    setFilters(current => {
      if (areaInsight.drillDownFilter === 'state') {
        return {
          ...current,
          state: areaInsight.label,
          district: 'All',
        };
      }

      if (areaInsight.drillDownFilter === 'district') {
        return {
          ...current,
          district: areaInsight.label,
        };
      }

      if (areaInsight.drillDownFilter === 'residence') {
        return {
          ...current,
          residence: areaInsight.label,
        };
      }

      return current;
    });
  };

  const hasGeneratedRows = clusterSegments.length > 0 && Boolean(dashboardData?.clusters?.length);
  const dashboardState = status === 'ready' && !hasGeneratedRows ? 'empty' : status;

  if (dashboardState !== 'ready') {
    return (
      <Container maxW="container.2xl" px={['4', '6', '8']} pt="4" pb="8" minH="100vh">
        <DashboardGuide />
        <DashboardStatePanel status={dashboardState} />
      </Container>
    );
  }

  return (
    <Container maxW="container.2xl" px={['4', '6', '8']} pt="4" pb="8" minH="100vh">
      {tier === 'demo' && <DemoBanner message={dashboardData?.metadata?.disclaimer} />}
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
            districts={districtIndicators.districts}
            indicator={filters.indicator}
            mapMode={filters.mapMode}
            onMapModeChange={value => updateFilter('mapMode', value)}
            onDistrictNavigate={record => navigate(`/state/${record.state_slug}/district/${record.district_slug}`)}
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
            selectedPriorityArea={selectedPriorityArea}
            status={status}
            summary={filteredSummary}
            areaInsight={areaInsight}
            onFilterChange={updateFilter}
            onResetFilters={resetFilters}
            onDrillIntoArea={drillIntoArea}
            onSelectPriorityArea={area => setSelectedPriorityAreaLabel(area.label)}
          />
        </Box>
      </Flex>
    </Container>
  );
};

export default Dashboard;
