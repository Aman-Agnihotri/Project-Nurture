import { Box, Button, Container, HStack, Text } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const Footer = () => {
  return (
    <Box as="footer" borderTopWidth="1px" borderColor="app.borderStrong" bg="app.bg">
      <Container maxW="container.2xl" px={['4', '6', '8']} py="6">
        <HStack justifyContent="space-between" alignItems="center" flexWrap="wrap" gap="3">
          <Box>
            <Text color="app.text" fontWeight="800">
              Project Nurture
            </Text>
            <Text color="app.subtle" fontSize="sm">
              A local DHS child nutrition explorer with a privacy-aware data boundary.
            </Text>
          </Box>
          <HStack spacing="2">
            <Button as={RouterLink} to="/dashboard" colorScheme="teal" size="sm" variant="ghost">
              Explorer
            </Button>
            <Button as={RouterLink} to="/about" colorScheme="teal" size="sm" variant="ghost">
              About
            </Button>
          </HStack>
        </HStack>
      </Container>
    </Box>
  );
};

export default Footer;
