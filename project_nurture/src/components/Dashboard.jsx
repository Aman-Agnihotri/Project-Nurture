import { Container, Flex, Box } from '@chakra-ui/react';
import MapComponent from './MapComponent';
import ModelComponent from './ModelComponent';

const Dashboard = () => {
  return (
    <Container maxW="container.2xl" px={['4', '6', '8']} py="20" minH="100vh">
      <Flex direction={['column', 'column', 'row']} gap="6" alignItems="stretch">
        <Box flex="1.75" minW="0">
          <MapComponent />
        </Box>
        <Box flex="1" minW={['full', 'full', '360px']}>
          <ModelComponent />
        </Box>
      </Flex>
    </Container>
  );
};

export default Dashboard;
