import {
  Alert,
  AlertIcon,
  Badge,
  Box,
  Divider,
  Heading,
  HStack,
  Select,
  SimpleGrid,
  Spinner,
  Stat,
  StatHelpText,
  StatLabel,
  StatNumber,
  Text,
  VStack,
} from '@chakra-ui/react';
import PropTypes from 'prop-types';
import {
  formatCount,
  formatPercent,
  metricLabel,
  metricOptions,
} from '../lib/nutritionData';

const coreMetrics = [
  ['stunting_rate', 'Stunted'],
  ['underweight_rate', 'Underweight'],
  ['wasting_rate', 'Wasted'],
  ['anemia_rate', 'Anemia'],
];

const FilterSelect = ({ label, value, options, onChange }) => (
  <Box>
    <Text fontSize="xs" color="gray.600" mb="1" fontWeight="semibold">
      {label}
    </Text>
    <Select size="sm" value={value} onChange={event => onChange(event.target.value)}>
      <option value="All">All</option>
      {options.map(option => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </Select>
  </Box>
);

FilterSelect.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.string).isRequired,
  onChange: PropTypes.func.isRequired,
};

const ModelComponent = ({
  dashboardData,
  filterOptions,
  filteredClusters,
  filters,
  status,
  summary,
  onFilterChange,
}) => {
  if (status === 'loading') {
    return (
      <VStack alignItems="flex-start" spacing="4" p="6">
        <Spinner color="teal.500" />
        <Text color="gray.600">Loading India DHS extract...</Text>
      </VStack>
    );
  }

  if (status === 'missing') {
    return (
      <Alert status="info" borderRadius="md" alignItems="flex-start">
        <AlertIcon />
        <Box>
          <Heading size="sm" mb="1">
            DHS extract not generated
          </Heading>
          <Text fontSize="sm">
            Run <code>python python_backend/dhs_pipeline.py</code> to create the local dashboard extract from approved DHS files.
          </Text>
        </Box>
      </Alert>
    );
  }

  const topClusters = [...filteredClusters]
    .filter(cluster => Number.isFinite(Number(cluster[filters.indicator])))
    .sort((a, b) => Number(b[filters.indicator]) - Number(a[filters.indicator]))
    .slice(0, 5);

  return (
    <VStack alignItems="stretch" spacing="6">
      <Box>
        <HStack justifyContent="space-between" alignItems="flex-start" gap="4">
          <Box>
            <Heading size="lg">India DHS Child Nutrition</Heading>
            <Text color="gray.600" mt="2">
              Standard DHS 2019-21, de facto children age 0-59 months
            </Text>
          </Box>
          <Badge colorScheme="teal" borderRadius="full" px="3" py="1">
            Local DHS extract
          </Badge>
        </HStack>
      </Box>

      <Box>
        <Heading size="sm" mb="3">
          Explorer Filters
        </Heading>
        <SimpleGrid columns={[1, 2]} spacing="3">
          <Box>
            <Text fontSize="xs" color="gray.600" mb="1" fontWeight="semibold">
              Map indicator
            </Text>
            <Select
              size="sm"
              value={filters.indicator}
              onChange={event => onFilterChange('indicator', event.target.value)}
            >
              {metricOptions.map(metric => (
                <option key={metric.key} value={metric.key}>
                  {metric.label}
                </option>
              ))}
            </Select>
          </Box>

          <FilterSelect
            label="State / UT"
            value={filters.state}
            options={filterOptions.states}
            onChange={value => onFilterChange('state', value)}
          />
          <FilterSelect
            label="District"
            value={filters.district}
            options={filterOptions.districts}
            onChange={value => onFilterChange('district', value)}
          />
          <FilterSelect
            label="Residence"
            value={filters.residence}
            options={filterOptions.residences}
            onChange={value => onFilterChange('residence', value)}
          />
          <FilterSelect
            label="Sex"
            value={filters.sex}
            options={filterOptions.sexes}
            onChange={value => onFilterChange('sex', value)}
          />
          <FilterSelect
            label="Wealth"
            value={filters.wealth}
            options={filterOptions.wealth}
            onChange={value => onFilterChange('wealth', value)}
          />
          <FilterSelect
            label="Age band"
            value={filters.ageBand}
            options={filterOptions.ageBands}
            onChange={value => onFilterChange('ageBand', value)}
          />
        </SimpleGrid>
      </Box>

      <SimpleGrid columns={[2, 2]} spacing="3">
        {coreMetrics.map(([key, label]) => (
          <Stat
            key={key}
            p="4"
            borderWidth="1px"
            borderColor="blackAlpha.200"
            borderRadius="md"
          >
            <StatLabel>{label}</StatLabel>
            <StatNumber fontSize="2xl">{formatPercent(summary[key])}</StatNumber>
            <StatHelpText mb="0">weighted mapped rate</StatHelpText>
          </Stat>
        ))}
      </SimpleGrid>

      <Box>
        <Heading size="sm" mb="3">
          Highest {metricLabel(filters.indicator)}
        </Heading>
        <VStack alignItems="stretch" spacing="3">
          {topClusters.map(cluster => (
            <HStack key={cluster.cluster_id} justifyContent="space-between" gap="4">
              <Box minW="0">
                <Text fontWeight="semibold" noOfLines={1}>
                  {cluster.district_name || 'DHS cluster'}
                </Text>
                <Text fontSize="sm" color="gray.600" noOfLines={1}>
                  {cluster.state_name} · {formatCount(cluster.child_count)} children
                </Text>
              </Box>
              <Badge colorScheme="orange" borderRadius="full" px="3" py="1">
                {formatPercent(cluster[filters.indicator])}
              </Badge>
            </HStack>
          ))}
          {topClusters.length === 0 && (
            <Text color="gray.600" fontSize="sm">
              No clusters match the selected filters.
            </Text>
          )}
        </VStack>
      </Box>

      <Divider />

      <SimpleGrid columns={[1, 2]} spacing="3">
        <Box>
          <Text fontSize="sm" color="gray.600">
            Mapped children in selection
          </Text>
          <Text fontSize="xl" fontWeight="bold">
            {formatCount(summary.child_count)}
          </Text>
        </Box>
        <Box>
          <Text fontSize="sm" color="gray.600">
            Mapped clusters
          </Text>
          <Text fontSize="xl" fontWeight="bold">
            {formatCount(filteredClusters.length)}
          </Text>
        </Box>
      </SimpleGrid>

      <Text fontSize="xs" color="gray.500">
        Rates use DHS sample weights. Cluster coordinates are displaced by DHS for respondent confidentiality. Filtered cuts are local aggregate views, not public redistributable data.
      </Text>
      <Text fontSize="xs" color="gray.400">
        Source: {dashboardData?.metadata?.survey || 'India Standard DHS, 2019-21'}
      </Text>
    </VStack>
  );
};

ModelComponent.propTypes = {
  dashboardData: PropTypes.shape({
    metadata: PropTypes.shape({
      survey: PropTypes.string,
    }),
  }),
  filterOptions: PropTypes.shape({
    states: PropTypes.arrayOf(PropTypes.string).isRequired,
    districts: PropTypes.arrayOf(PropTypes.string).isRequired,
    residences: PropTypes.arrayOf(PropTypes.string).isRequired,
    sexes: PropTypes.arrayOf(PropTypes.string).isRequired,
    wealth: PropTypes.arrayOf(PropTypes.string).isRequired,
    ageBands: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  filteredClusters: PropTypes.arrayOf(
    PropTypes.shape({
      cluster_id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      district_name: PropTypes.string,
      state_name: PropTypes.string,
      child_count: PropTypes.number,
      risk_score: PropTypes.number,
      stunting_rate: PropTypes.number,
      underweight_rate: PropTypes.number,
      wasting_rate: PropTypes.number,
      severe_wasting_rate: PropTypes.number,
      overweight_rate: PropTypes.number,
      anemia_rate: PropTypes.number,
    }),
  ).isRequired,
  filters: PropTypes.shape({
    indicator: PropTypes.string.isRequired,
    mapMode: PropTypes.string.isRequired,
    state: PropTypes.string.isRequired,
    district: PropTypes.string.isRequired,
    residence: PropTypes.string.isRequired,
    sex: PropTypes.string.isRequired,
    wealth: PropTypes.string.isRequired,
    ageBand: PropTypes.string.isRequired,
  }).isRequired,
  status: PropTypes.string.isRequired,
  summary: PropTypes.shape({
    child_count: PropTypes.number,
    stunting_rate: PropTypes.number,
    underweight_rate: PropTypes.number,
    wasting_rate: PropTypes.number,
    anemia_rate: PropTypes.number,
  }).isRequired,
  onFilterChange: PropTypes.func.isRequired,
};

export default ModelComponent;
