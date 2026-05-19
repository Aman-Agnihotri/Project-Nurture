import {
  Badge,
  Box,
  Button,
  Container,
  Heading,
  HStack,
  SimpleGrid,
  Stack,
  Text,
  VStack,
} from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';
import { FiArrowRight, FiDatabase, FiMap, FiShield, FiTrendingUp } from 'react-icons/fi';
import heroImage from '../assets/img4.jpg';

const featureItems = [
  {
    icon: FiDatabase,
    title: 'Survey-backed indicators',
    text: 'Uses a local India Standard DHS extract to summarize child nutrition rates with survey weights.',
  },
  {
    icon: FiMap,
    title: 'Spatial exploration',
    text: 'Maps displaced DHS clusters with filterable indicators, cluster aggregation, and optional heat layers.',
  },
  {
    icon: FiTrendingUp,
    title: 'Decision support',
    text: 'Ranks priority areas so the dashboard answers where to look first, not just what the map looks like.',
  },
  {
    icon: FiShield,
    title: 'Privacy-aware by design',
    text: 'Keeps restricted DHS data local and treats cluster coordinates as displaced survey locations.',
  },
];

const Home = () => {
  return (
    <Box>
      <Box
        minH="calc(100vh - 64px)"
        position="relative"
        bgImage={`linear-gradient(90deg, rgba(8, 47, 73, 0.84), rgba(8, 47, 73, 0.46)), url(${heroImage})`}
        bgPosition="center"
        bgSize="cover"
        color="white"
      >
        <Container maxW="container.xl" minH="calc(100vh - 64px)" px={['4', '6', '8']}>
          <Stack justifyContent="center" minH="calc(100vh - 64px)" maxW="3xl" spacing="7">
            <Badge alignSelf="flex-start" colorScheme="teal" px="3" py="1">
              India Standard DHS 2019-21
            </Badge>
            <VStack alignItems="flex-start" spacing="4">
              <Heading as="h1" fontSize={['4xl', '5xl', '6xl']} lineHeight="1">
                Project Nurture
              </Heading>
              <Text color="whiteAlpha.900" fontSize={['lg', 'xl']} maxW="2xl">
                A child nutrition intelligence dashboard that turns survey microdata into
                map-based exploration, priority ranking, and a foundation for future field follow-up.
              </Text>
            </VStack>
            <HStack flexWrap="wrap" gap="3">
              <Button
                as={RouterLink}
                to="/dashboard"
                colorScheme="teal"
                rightIcon={<FiArrowRight />}
                size="lg"
              >
                Open Explorer
              </Button>
              <Button
                as={RouterLink}
                to="/about"
                bg="whiteAlpha.200"
                color="white"
                size="lg"
                _hover={{ bg: 'whiteAlpha.300' }}
              >
                Project Context
              </Button>
            </HStack>
          </Stack>
        </Container>
      </Box>

      <Box bg="gray.50" py={['12', '16']}>
        <Container maxW="container.xl" px={['4', '6', '8']}>
          <SimpleGrid columns={[1, 2, 4]} spacing="5">
            {featureItems.map(item => {
              const Icon = item.icon;
              return (
                <Box
                  key={item.title}
                  bg="white"
                  borderRadius="md"
                  borderWidth="1px"
                  borderColor="blackAlpha.100"
                  p="5"
                >
                  <Icon color="#0f766e" size="24" />
                  <Heading color="gray.800" mt="4" size="sm">
                    {item.title}
                  </Heading>
                  <Text color="gray.600" fontSize="sm" mt="2">
                    {item.text}
                  </Text>
                </Box>
              );
            })}
          </SimpleGrid>
        </Container>
      </Box>
    </Box>
  );
};

export default Home;
