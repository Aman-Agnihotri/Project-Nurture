import { Container, Heading} from '@chakra-ui/react';
import React from 'react';
import MapComponent from './MapComponent';

const Dashboard = () => {
  return (
    <Container maxW={'container.xl'} p='16'>
      <Heading textTransform={"uppercase"} py='2' w="fit-content" borderBottom={'2px solid teal'} m='auto' fontSize='2xl'>
        "Welcome to the Dashboard"
      </Heading>
      <MapComponent />
    </Container>
  );
};

export default Dashboard;