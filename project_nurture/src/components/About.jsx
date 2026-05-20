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
    title: 'Problem frame',
    text: 'Project Nurture connects large-scale child health survey data with a practical view of areas that may need closer attention.',
  },
  {
    title: 'Public explorer',
    text: 'The current product focuses on aggregate DHS child nutrition indicators, map exploration, and planning-oriented priority views.',
  },
  {
    title: 'Private workflow',
    text: 'A future operational layer could connect field follow-up, case progress, and ground-worker workflows without exposing restricted survey data.',
  },
];

const About = () => {
  return (
    <Box bg="app.bg" minH="calc(100vh - 64px)" py={['12', '16']}>
      <Container maxW="container.xl" px={['4', '6', '8']}>
        <Stack spacing="8">
          <Box maxW="3xl">
            <Badge colorScheme="teal" mb="4">
              Project Context
            </Badge>
            <Heading color="app.heading" size="2xl">
              A child nutrition explorer with a clear public and private data boundary.
            </Heading>
            <Text color="app.muted" fontSize="lg" mt="4">
              Project Nurture uses India Standard DHS data to support aggregate exploration,
              priority scanning, and a future path toward secure field follow-up workflows.
            </Text>
          </Box>

          <SimpleGrid columns={[1, 3]} spacing="5">
            {contextItems.map(item => (
              <Box
                key={item.title}
                bg="app.surface"
                borderRadius="md"
                borderWidth="1px"
                borderColor="app.border"
                p="5"
              >
                <Heading color="app.text" size="sm">
                  {item.title}
                </Heading>
                <Text color="app.muted" fontSize="sm" mt="3">
                  {item.text}
                </Text>
              </Box>
            ))}
          </SimpleGrid>

          <Box bg="app.surface" borderRadius="md" borderWidth="1px" borderColor="app.border" p="6">
            <Heading color="app.text" size="md">
              Data boundary
            </Heading>
            <Text color="app.muted" mt="3">
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
