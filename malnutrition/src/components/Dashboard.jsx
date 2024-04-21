import { Box, Container, Heading, Text } from '@chakra-ui/react';
import React from 'react';
import MapComponent from './MapComponent';

const Dashboard = () => {
  return (
    <Container maxW={'container.xl'} p='16'>
      <Heading textTransform={"uppercase"} py='2' w="fit-content" borderBottom={'2px solid teal'} m='auto' fontSize='2xl'>
        "Welcome to the Dashboard"
      </Heading>
      <Box p='4'>
        <Text>
          "Here you can manage your account, view your progress, and much more..."
        </Text>
      </Box>
      <MapComponent />
    </Container>
  );
};

export default Dashboard;