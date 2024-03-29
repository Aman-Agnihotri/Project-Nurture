import React, { useState } from 'react';
import { Avatar, Button, Container, Heading, Input, Text, VStack } from '@chakra-ui/react';
  import { Link } from 'react-router-dom';
  import axios from 'axios';
  
  const Signup = () => {
    // State variables
    const [username, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e) => {
      e.preventDefault(); // Prevent default form submission

      const userData = {
        username, // Assuming the backend expects 'username' instead of 'name'
        password,
      };

      try {
        const response = await axios.post('http://localhost:3000/users/signup', userData);
        console.log(response.data);
        // Handle successful signup (e.g., redirect to login page)
      } catch (error) {
        console.error('Error signing up:', error);
        // Handle errors (e.g., show an error message)
      }
    };
    return (
      <Container maxW={'container.xl'} h={'100vh'} p={'16'}>
        <form onSubmit={handleSubmit}>
          <VStack
            alignItems={'stretch'}
            spacing={'8'}
            w={['full', '96']}
            m={'auto'}
            my={'16'}
          >
            <Heading>VIDEO HUB</Heading>
            <Avatar alignSelf={'center'} boxSize={'32'} />
  
            <Input
              placeholder={'Name'}
              type={'text'}
              required
              focusBorderColor={' teal.500'}
              value={username}
              onChange={(e) => setName(e.target.value)}
            />
            <Input
              placeholder={'Email'}
              type={'email'}
              required
              focusBorderColor={' teal.500'}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              placeholder={'Password'}
              type={'password'}
              required
              focusBorderColor={' teal.500'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
  
            <Button colorScheme={' teal'} type={'submit'}>
              Sign Up
            </Button>
  
            <Text textAlign={'right'}>
              Already Signed Up?{' '}
              <Button variant={'link'} colorScheme={' teal'}>
                <Link to={'/login'}>Login In</Link>
              </Button>
            </Text>
          </VStack>
        </form>
      </Container>
    );
  };
  
  export default Signup;