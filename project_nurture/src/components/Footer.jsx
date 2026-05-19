import { Box, Button, Container, HStack, Text } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const Footer = () => {
  return (
    <Box as="footer" borderTopWidth="1px" borderColor="blackAlpha.200" bg="gray.50">
      <Container maxW="container.2xl" px={['4', '6', '8']} py="6">
        <HStack justifyContent="space-between" alignItems="center" flexWrap="wrap" gap="3">
          <Box>
            <Text color="gray.800" fontWeight="800">
              Project Nurture
            </Text>
            <Text color="gray.500" fontSize="sm">
              A local DHS child nutrition explorer and portfolio data product.
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
