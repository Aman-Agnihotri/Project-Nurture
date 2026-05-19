import {
  Button,
  Container,
  Heading,
  Input,
  Text,
  VStack,
} from '@chakra-ui/react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from "react-toastify";
import { signInWithEmailAndPassword } from "firebase/auth";
import { authSessionTtlMs, createAuthSession } from '../lib/authSession';
import { auth } from "../lib/firebase";

const getSafeRedirectPath = search => {
  const redirect = new URLSearchParams(search).get('redirect');

  if (!redirect || !redirect.startsWith('/') || redirect.startsWith('//')) {
    return '/dashboard';
  }

  return redirect;
};

const Login = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const redirectPath = getSafeRedirectPath(location.search);
  const sessionHours = Math.round(authSessionTtlMs / 60 / 60 / 1000);

  const handleLogin = async (event) => {
    event.preventDefault();
  
    const formData = new FormData(event.target);
    const { email, password } = Object.fromEntries(formData);
  
    try {
      const credential = await signInWithEmailAndPassword(auth, email, password);
      createAuthSession(credential.user.uid);
      toast.success('Login successful!', {
        position: "bottom-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      navigate(redirectPath, { replace: true });
    } catch (err) {
      toast.error('Login failed: ' + err.message, {
        position: "bottom-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
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
          <Text color="gray.600" fontSize="sm">
            Dashboard access stays active for {sessionHours} hours on this device.
          </Text>

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
