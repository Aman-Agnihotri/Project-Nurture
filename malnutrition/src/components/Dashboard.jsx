// Dashboard.jsx
import { Container, Heading} from '@chakra-ui/react';
import React from 'react';
import MapComponent from './MapComponent';

const Dashboard = () => {
  return (
    <Container maxW={'container.xl'} p='16'>
      <MapComponent />
    </Container>
  );
};

export default Dashboard;