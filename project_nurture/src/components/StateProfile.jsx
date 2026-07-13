import { Box, Button, Container, Heading, HStack, Link, Table, TableContainer, Tbody, Td, Text, Th, Thead, Tr } from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { loadDistrictIndicators } from '../lib/dataSource';
import { formatPercent, profileMetricOptions } from '../lib/nutritionData';
import { buildSlugLookup } from '../lib/slugs';

const baseUrl = import.meta.env.BASE_URL || '/';

const StateProfile = () => {
  const { stateSlug } = useParams();
  const [data, setData] = useState(null);
  const [sort, setSort] = useState({ key: 'risk_score', direction: 'desc' });
  useEffect(() => { loadDistrictIndicators(baseUrl).then(setData).catch(() => setData({ districts: [], states: [] })); }, []);
  const lookup = useMemo(() => buildSlugLookup(data?.districts), [data]);
  const stateName = lookup.stateBySlug.get(stateSlug);
  const state = data?.states?.find(row => row.state_slug === stateSlug || row.state_name === stateName);
  const districts = useMemo(() => (data?.districts || []).filter(row => row.state_name === stateName).sort((left, right) => (Number(right[sort.key]) - Number(left[sort.key])) * (sort.direction === 'desc' ? 1 : -1)), [data, sort, stateName]);
  if (!data) return <Container py="10"><Text>Loading public demo profile…</Text></Container>;
  if (!stateName || !state) return <Container py="10"><Heading size="lg">State coverage unavailable</Heading><Text mt="3">This state slug is not included in the current public demo artifact.</Text><Link as={RouterLink} to="/dashboard">Return to dashboard</Link></Container>;
  const changeSort = key => setSort(current => ({ key, direction: current.key === key && current.direction === 'desc' ? 'asc' : 'desc' }));
  return <Container maxW="container.xl" py="8"><Text fontSize="sm"><Link as={RouterLink} to="/">Home</Link> → State</Text><HStack justify="space-between" align="start" mt="3"><Box><Heading>{stateName}</Heading><Text color="app.muted">Unweighted public demo district rollup; values are placeholders.</Text></Box><Button as={RouterLink} to={`/dashboard?state=${encodeURIComponent(state.state_slug)}`}>View on dashboard</Button></HStack><Heading size="md" mt="8">State and national comparison</Heading><HStack align="stretch" wrap="wrap" mt="3">{profileMetricOptions.map(metric => <Box key={metric.key} p="3" minW="150px" borderWidth="1px" borderRadius="md"><Text fontSize="sm">{metric.label}</Text><Text fontWeight="bold">{formatPercent(state[metric.key])}</Text><Text fontSize="xs" color="app.muted">National {formatPercent(data.national?.[metric.key])}</Text></Box>)}</HStack><Heading size="md" mt="8">Districts</Heading>{districts.length ? <TableContainer mt="3"><Table size="sm"><Thead><Tr><Th>District</Th>{profileMetricOptions.map(metric => <Th key={metric.key}><Button size="xs" variant="ghost" onClick={() => changeSort(metric.key)}>{metric.label}</Button></Th>)}</Tr></Thead><Tbody>{districts.map((district, index) => <Tr key={district.district_slug} bg={index === 0 ? 'red.50' : index === districts.length - 1 ? 'blue.50' : undefined}><Td><Link as={RouterLink} to={`/state/${stateSlug}/district/${district.district_slug}`}>{district.district_name}</Link></Td>{profileMetricOptions.map(metric => <Td key={metric.key}>{formatPercent(district[metric.key])}</Td>)}</Tr>)}</Tbody></Table></TableContainer> : <Text mt="3">No district records are available for this state in the public demo.</Text>}</Container>;
};

export default StateProfile;
