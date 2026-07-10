import { Badge, Box, Container, HStack, Text, VStack } from '@chakra-ui/react';

const Footer = () => {
  return (
    <Box as="footer" bg="app.surface" borderTopWidth="1px" borderColor="app.borderStrong">
      <Container maxW="container.2xl" px={['4', '6', '8']} py={['5', '6']}>
        <VStack alignItems="stretch" spacing="3">
          <HStack flexWrap="wrap" gap="2">
            <Badge colorScheme="teal">Public explorer</Badge>
            <Badge colorScheme="purple">Local DHS extract</Badge>
            <Badge colorScheme="orange">Private workflow concept</Badge>
          </HStack>

          <Text color="app.text" fontSize="sm" fontWeight="semibold">
            Project Nurture uses locally generated India Standard DHS 2019-21 aggregates for
            child nutrition exploration.
          </Text>
          <Text color="app.subtle" fontSize="xs" maxW="container.lg">
            DHS GPS points are displaced for confidentiality. Restricted DHS microdata and
            generated extracts are not redistributed from this public version.
          </Text>
        </VStack>
      </Container>
    </Box>
  );
};

export default Footer;
