import {
  Button,
  Container,
  Heading,
  Input,
  Text,
  VStack,
} from '@chakra-ui/react';
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
// import { toast } from "react-toastify";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../lib/firebase";

const Login = () => {
  const navigate = useNavigate();

  const handleLogin = async (event) => {
    event.preventDefault();

    const formData = new FormData(event.target);
    const { email, password } = Object.fromEntries(formData);

    try {
      await signInWithEmailAndPassword(auth, email, password);
      console.log('Login successful');
      navigate('/dashboard');
      } catch (err) {
      // toast.warn(err.message);
      console.log(err);
    }
  };

  return (
    <Container maxW={'container.xl'} h={'100vh'} p={'16'}>
      <form onSubmit={handleLogin}>
        <VStack
          alignItems={'stretch'}
          spacing={'8'}
          w={['full', '96']}
          m={'auto'}
          my={'16'}
        >
          <Heading>Welcome Back</Heading>

          <Input
            placeholder={'Email Address'}
            type={'text'}
            required = {true}
            focusBorderColor={' teal.500'}
            name= {"email"}
          />
          <Input
            placeholder={'Password'}
            type={'password'}
            required = {true}
            focusBorderColor={' teal.500'}
            name={"password"}
          />

          <Button variant={'link'} alignSelf={'flex-end'}>
            <Link to={'/forgetpassword'}>Forget Password?</Link>
          </Button>

          <Button colorScheme={' teal'} type={'submit'}>
            Log In
          </Button>

          <Text textAlign={'right'}>
            New User?{' '}
            <Button variant={'link'} colorScheme={' teal'}>
              <Link to={'/signup'}>Sign Up</Link>
            </Button>
          </Text>
        </VStack>
      </form>
    </Container>
  );
};

export default Login;