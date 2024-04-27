// Dashboard.jsx
import { Container, Flex, Box } from '@chakra-ui/react';
import MapComponent from './MapComponent';
import ModelComponent from './ModelComponent';

const Dashboard = () => {
  return (
    <Container maxW={'container.xl'} p='16' height="100vh"> {/* Set the height to 100vh */}
      <Flex direction={['column', 'row']} justifyContent="space-between" height="100%"> {/* Adjust the Flex container */}
        <Box flex='1' flexGrow='1' marginRight='16'>
          <MapComponent />
        </Box>
        <Box flex='1'>
          <ModelComponent />
        </Box>
      </Flex>
    </Container>
  );
};

export default Dashboard;