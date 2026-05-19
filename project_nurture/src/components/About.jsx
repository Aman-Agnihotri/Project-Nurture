import {
  Badge,
  Box,
  Container,
  Heading,
  SimpleGrid,
  Stack,
  Text,
} from '@chakra-ui/react';

const contextItems = [
  {
    title: 'Original motivation',
    text: 'The project began as an attempt to connect large-scale child health survey data with a practical view of areas that may need closer attention.',
  },
  {
    title: 'Current focus',
    text: 'The public version now focuses on aggregate DHS child nutrition indicators, map exploration, and planning-oriented priority views.',
  },
  {
    title: 'Future direction',
    text: 'A private operational version could connect field follow-up, case progress, and ground-worker workflows without exposing restricted survey data.',
  },
];

const About = () => {
  return (
    <Box bg="gray.50" minH="calc(100vh - 64px)" py={['12', '16']}>
      <Container maxW="container.xl" px={['4', '6', '8']}>
        <Stack spacing="8">
          <Box maxW="3xl">
            <Badge colorScheme="teal" mb="4">
              Project Context
            </Badge>
            <Heading color="gray.900" size="2xl">
              From college proof of concept to a focused public-health data product.
            </Heading>
            <Text color="gray.600" fontSize="lg" mt="4">
              Project Nurture is being rebuilt around real India Standard DHS data, with a
              clearer separation between what can be shown publicly and what would belong
              in a private field operations system.
            </Text>
          </Box>

          <SimpleGrid columns={[1, 3]} spacing="5">
            {contextItems.map(item => (
              <Box
                key={item.title}
                bg="white"
                borderRadius="md"
                borderWidth="1px"
                borderColor="blackAlpha.100"
                p="5"
              >
                <Heading color="gray.800" size="sm">
                  {item.title}
                </Heading>
                <Text color="gray.600" fontSize="sm" mt="3">
                  {item.text}
                </Text>
              </Box>
            ))}
          </SimpleGrid>

          <Box bg="white" borderRadius="md" borderWidth="1px" borderColor="blackAlpha.100" p="6">
            <Heading color="gray.800" size="md">
              Data boundary
            </Heading>
            <Text color="gray.600" mt="3">
              The dashboard is designed to work with locally generated aggregates from
              restricted DHS files. The repository should contain code, documentation, and
              public-safe examples, not raw DHS microdata or generated restricted extracts.
            </Text>
          </Box>
        </Stack>
      </Container>
    </Box>
  );
};

export default About;
