import {
  Button,
  Container,
  Heading,
  Input,
  Text,
  VStack,
} from '@chakra-ui/react';
import { useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from "react-toastify";
import { onAuthStateChanged, signInWithEmailAndPassword } from "firebase/auth";
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

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      if (user) {
        navigate(redirectPath, { replace: true });
      }
    });

    return unsubscribe;
  }, [navigate, redirectPath]);

  const handleLogin = async (event) => {
    event.preventDefault();
  
    const formData = new FormData(event.target);
    const { email, password } = Object.fromEntries(formData);
  
    try {
      await signInWithEmailAndPassword(auth, email, password);
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
    <Container maxW={'container.xl'} minH={'100vh'} p={['6', '10', '16']}>
      <form onSubmit={handleLogin}>
        <VStack
          alignItems={'stretch'}
          spacing={'8'}
          w={['full', '96']}
          m={'auto'}
          my={['10', '14', '16']}
        >
          <Heading>Access Project Nurture</Heading>
          <Text color="app.muted" fontSize="sm">
            Sign in to open the India DHS child nutrition explorer.
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
            <Link to={'/forgetpassword'}>Forgot password?</Link>
          </Button>

          <Button colorScheme={' teal'} type={'submit'}>
            Log In
          </Button>

          <Text textAlign={'right'}>
            Need access?{' '}
            <Button variant={'link'} colorScheme={' teal'}>
              <Link to={'/signup'}>Create account</Link>
            </Button>
          </Text>
        </VStack>
      </form>
    </Container>
  );
};

export default Login;
