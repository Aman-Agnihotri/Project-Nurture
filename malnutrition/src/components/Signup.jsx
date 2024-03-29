import {
  Avatar,
  Button,
  Container,
  Heading,
  Input,
  Text,
  VStack,
} from '@chakra-ui/react';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

axios.defaults.baseURL = 'http://localhost:3000';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await axios.post('/users/register', {
        username,
        email,
        password,
      });

      if (response.status === 201) {
        console.log('Signup successful');
        navigate('/login');
      } else {
        console.error('Signup failed');
      }
    } catch (error) {
      console.error('An error occurred while signing up:', error);
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
            onChange={(event) => setUsername(event.target.value)}
          />
          <Input
            placeholder={'Email'}
            type={'email'}
            required
            focusBorderColor={' teal.500'}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <Input
            placeholder={'Password'}
            type={'password'}
            required
            focusBorderColor={' teal.500'}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <Text textAlign={'right'}>
              Already Signed Up?{' '}
              <Button variant={'link'} colorScheme={' teal'}>
                <Link to={'/login'}>Login In</Link>
              </Button>
            </Text>
          <Button colorScheme={' teal'} type="submit">Sign Up</Button>
        </VStack>
      </form>
    </Container>
  );
};

export default Signup;