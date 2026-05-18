import {
  Alert,
  AlertIcon,
  Badge,
  Box,
  Divider,
  Heading,
  HStack,
  SimpleGrid,
  Spinner,
  Stat,
  StatHelpText,
  StatLabel,
  StatNumber,
  Text,
  VStack,
} from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';

const baseUrl = import.meta.env.BASE_URL || '/';
const dhsDataUrl = `${baseUrl}generated/dhs_cluster_nutrition.json`;

const metrics = [
  ['stunting_rate', 'Stunted'],
  ['underweight_rate', 'Underweight'],
  ['wasting_rate', 'Wasted'],
  ['anemia_rate', 'Anemia'],
];

const formatPercent = value => {
  const number = Number(value);
  return Number.isFinite(number) ? `${number.toFixed(1)}%` : 'No data';
};

const formatCount = value => {
  const number = Number(value);
  return Number.isFinite(number) ? number.toLocaleString('en-IN') : '0';
};

const ModelComponent = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [status, setStatus] = useState('loading');

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

  const highestRiskStates = useMemo(() => {
    if (!dashboardData?.states) return [];

    return [...dashboardData.states]
      .filter(state => Number.isFinite(Number(state.risk_score)))
      .sort((a, b) => Number(b.risk_score) - Number(a.risk_score))
      .slice(0, 5);
  }, [dashboardData]);

  if (status === 'loading') {
    return (
      <VStack alignItems="flex-start" spacing="4" p="6">
        <Spinner color="teal.500" />
        <Text color="gray.600">Loading NFHS-5 extract...</Text>
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
            Run <code>python python_backend/dhs_pipeline.py</code> to create the local dashboard extract from approved DHS/NFHS-5 files.
          </Text>
        </Box>
      </Alert>
    );
  }

  return (
    <VStack alignItems="stretch" spacing="6">
      <Box>
        <HStack justifyContent="space-between" alignItems="flex-start" gap="4">
          <Box>
            <Heading size="lg">NFHS-5 Child Nutrition</Heading>
            <Text color="gray.600" mt="2">
              India DHS 2019-21, de facto children age 0-59 months
            </Text>
          </Box>
          <Badge colorScheme="teal" borderRadius="full" px="3" py="1">
            Local DHS extract
          </Badge>
        </HStack>
      </Box>

      <SimpleGrid columns={[2, 2]} spacing="3">
        {metrics.map(([key, label]) => (
          <Stat
            key={key}
            p="4"
            borderWidth="1px"
            borderColor="blackAlpha.200"
            borderRadius="md"
          >
            <StatLabel>{label}</StatLabel>
            <StatNumber fontSize="2xl">{formatPercent(dashboardData.national[key])}</StatNumber>
            <StatHelpText mb="0">weighted national rate</StatHelpText>
          </Stat>
        ))}
      </SimpleGrid>

      <Box>
        <Heading size="sm" mb="3">
          Highest Composite Risk
        </Heading>
        <VStack alignItems="stretch" spacing="3">
          {highestRiskStates.map(state => (
            <HStack key={state.state_code} justifyContent="space-between">
              <Box>
                <Text fontWeight="semibold">{state.state_name}</Text>
                <Text fontSize="sm" color="gray.600">
                  {formatCount(state.haz_valid_n)} valid child measurements
                </Text>
              </Box>
              <Badge colorScheme="orange" borderRadius="full" px="3" py="1">
                {formatPercent(state.risk_score)}
              </Badge>
            </HStack>
          ))}
        </VStack>
      </Box>

      <Divider />

      <SimpleGrid columns={[1, 2]} spacing="3">
        <Box>
          <Text fontSize="sm" color="gray.600">
            Children in extract
          </Text>
          <Text fontSize="xl" fontWeight="bold">
            {formatCount(dashboardData.national.child_count)}
          </Text>
        </Box>
        <Box>
          <Text fontSize="sm" color="gray.600">
            Mapped clusters
          </Text>
          <Text fontSize="xl" fontWeight="bold">
            {formatCount(dashboardData.clusters.length)}
          </Text>
        </Box>
      </SimpleGrid>

      <Text fontSize="xs" color="gray.500">
        Rates use DHS sample weights. Cluster coordinates are displaced by DHS for respondent confidentiality.
      </Text>
    </VStack>
  );
};

export default ModelComponent;
