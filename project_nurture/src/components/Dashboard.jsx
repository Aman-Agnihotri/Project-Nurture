// Dashboard.jsx
import { Container } from '@chakra-ui/react';
import MapComponent from './MapComponent';

const Dashboard = () => {
  return (
    <Container maxW={'container.xl'} p='16'>
      <MapComponent />
    </Container>
  );
};

export default Dashboard;