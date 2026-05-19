import { Container, Spinner, Text, VStack } from '@chakra-ui/react';
import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { clearAuthSession, hasFreshAuthSession } from '../lib/authSession';
import { auth } from '../lib/firebase';

const RequireAuth = ({ children }) => {
  const location = useLocation();
  const [state, setState] = useState({
    checking: true,
    isAuthorized: false,
  });

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      const isAuthorized = Boolean(user && hasFreshAuthSession(user.uid));

      if (user && !isAuthorized) {
        clearAuthSession();
        signOut(auth).catch(() => {});
      }

      setState({
        checking: false,
        isAuthorized,
      });
    });

    return unsubscribe;
  }, []);

  if (state.checking) {
    return (
      <Container maxW="container.md" py="24">
        <VStack spacing="4">
          <Spinner color="teal.500" />
          <Text color="gray.600">Checking dashboard access...</Text>
        </VStack>
      </Container>
    );
  }

  if (!state.isAuthorized) {
    const redirectPath = `${location.pathname}${location.search}`;
    return (
      <Navigate
        replace
        to={`/login?redirect=${encodeURIComponent(redirectPath)}`}
      />
    );
  }

  return children;
};

RequireAuth.propTypes = {
  children: PropTypes.node.isRequired,
};

export default RequireAuth;
