import { Badge, Box, Container, Heading, HStack, Link, Text } from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { loadDistrictIndicators } from '../lib/dataSource';
import { formatPercent, metricOptions, planningFocusRules, profileMetricOptions } from '../lib/nutritionData';
import { buildSlugLookup } from '../lib/slugs';

const baseUrl = import.meta.env.BASE_URL || '/';

const DistrictProfile = () => {
  const { stateSlug, districtSlug } = useParams();
  const [data, setData] = useState(null);
  useEffect(() => { loadDistrictIndicators(baseUrl).then(setData).catch(() => setData({ districts: [], states: [] })); }, []);
  const lookup = useMemo(() => buildSlugLookup(data?.districts), [data]);
  const district = lookup.districtBySlug.get(`${stateSlug}/${districtSlug}`);
  const state = data?.states?.find(row => row.state_slug === stateSlug);
  if (!data) return <Container py="10"><Text>Loading public demo profile…</Text></Container>;
  if (!district || !state) return <Container py="10"><Heading size="lg">District coverage unavailable</Heading><Text mt="3">This state or district is not included in the current public demo artifact.</Text><Link as={RouterLink} to="/dashboard">Return to dashboard</Link></Container>;
  const drivers = new Map(metricOptions.map(metric => [metric.key, { value: district[metric.key], delta: Number(district[metric.key]) - Number(state[metric.key]) }]));
  const focuses = planningFocusRules.filter(rule => rule.matches(drivers));
  return <Container maxW="container.lg" py="8"><Text fontSize="sm"><Link as={RouterLink} to="/">Home</Link> → <Link as={RouterLink} to={`/state/${stateSlug}`}>{state.state_name}</Link> → District</Text><Heading mt="3">{district.district_name}</Heading><Text color="app.muted">Public demo values are placeholders and support planning-style exploration only.</Text><Heading size="md" mt="8">District, state, and national comparison</Heading><Box mt="3" display="grid" gridTemplateColumns={['1fr', 'repeat(3, 1fr)']} gap="3">{profileMetricOptions.map(metric => <Box key={metric.key} p="3" borderWidth="1px" borderRadius="md"><Text fontWeight="bold">{metric.label}</Text><Text>District: {formatPercent(district[metric.key])}</Text><Text fontSize="sm">State: {formatPercent(state[metric.key])}</Text><Text fontSize="sm">National: {formatPercent(data.national?.[metric.key])}</Text></Box>)}</Box><Heading size="md" mt="8">Planning focus</Heading><HStack mt="3" wrap="wrap">{focuses.length ? focuses.map(focus => <Badge key={focus.label} colorScheme={focus.colorScheme} title={focus.description}>{focus.label}</Badge>) : <Text>No single planning focus stands out in this partial demo coverage.</Text>}</HStack></Container>;
};

export default DistrictProfile;
