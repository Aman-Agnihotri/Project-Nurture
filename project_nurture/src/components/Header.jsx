import {
  Box,
  Button,
  Badge,
  Container,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerHeader,
  DrawerOverlay,
  Flex,
  HStack,
  IconButton,
  Text,
  useDisclosure,
  VStack,
} from '@chakra-ui/react';
import PropTypes from 'prop-types';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { FiLogOut, FiMenu } from 'react-icons/fi';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { useEffect, useState } from 'react';
import ColorModeSwitcher from '../ColorModeSwitcher';
import { clearAuthSession, hasFreshAuthSession } from '../lib/authSession';
import { auth } from '../lib/firebase';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Explorer', to: '/dashboard' },
  { label: 'Private Workflow', to: '/form' },
  { label: 'About', to: '/about' },
];

const NavButton = ({ item, onClick }) => (
  <Button
    as={RouterLink}
    to={item.to}
    variant="ghost"
    colorScheme="teal"
    size="sm"
    onClick={onClick}
  >
    {item.label}
  </Button>
);

NavButton.propTypes = {
  item: PropTypes.shape({
    label: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
  }).isRequired,
  onClick: PropTypes.func,
};

const Header = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const navigate = useNavigate();
  const [authUser, setAuthUser] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, user => {
      setAuthUser(user && hasFreshAuthSession(user.uid) ? user : null);
    });

    return unsubscribe;
  }, []);

  const handleLogout = async () => {
    clearAuthSession();
    await signOut(auth).catch(() => {});
    onClose();
    navigate('/login', { replace: true });
  };

  return (
    <Box
      as="header"
      position="sticky"
      top="0"
      zIndex="sticky"
      borderBottomWidth="1px"
      borderColor="app.borderStrong"
      bg="app.headerBg"
      backdropFilter="blur(14px)"
    >
      <Container maxW="container.2xl" px={['4', '6', '8']}>
        <Flex minH="16" alignItems="center" justifyContent="space-between" gap="4">
          <HStack spacing="3" minW="0">
            <IconButton
              aria-label="Open navigation"
              display={['inline-flex', 'inline-flex', 'none']}
              icon={<FiMenu />}
              onClick={onOpen}
              size="sm"
              variant="ghost"
            />
            <Box minW="0">
              <Text
                as={RouterLink}
                to="/"
                color="app.brand"
                display="block"
                fontSize="lg"
                fontWeight="800"
                lineHeight="1.1"
              >
                Project Nurture
              </Text>
              <Text color="app.subtle" fontSize="xs" noOfLines={1}>
                India DHS child nutrition explorer
              </Text>
            </Box>
          </HStack>

          <HStack spacing="2" display={['none', 'none', 'flex']}>
            {navItems.map(item => (
              <NavButton key={item.to} item={item} />
            ))}
          </HStack>

          <HStack spacing="2">
            {authUser ? (
              <>
                <Badge colorScheme="teal" display={['none', 'none', 'inline-flex']} px="3" py="1">
                  Signed in
                </Badge>
                <Button
                  colorScheme="teal"
                  display={['none', 'inline-flex']}
                  leftIcon={<FiLogOut />}
                  onClick={handleLogout}
                  size="sm"
                  variant="outline"
                >
                  Logout
                </Button>
              </>
            ) : (
              <Button
                as={RouterLink}
                to="/login"
                colorScheme="teal"
                display={['none', 'inline-flex']}
                size="sm"
              >
                Login
              </Button>
            )}
            <ColorModeSwitcher
              aria-label="Toggle color mode"
              pos="static"
              top="auto"
              right="auto"
              size="sm"
            />
          </HStack>
        </Flex>
      </Container>

      <Drawer isOpen={isOpen} onClose={onClose} placement="left">
        <DrawerOverlay />
        <DrawerContent bg="app.surface">
          <DrawerCloseButton />
          <DrawerHeader>Project Nurture</DrawerHeader>
          <DrawerBody>
            <VStack alignItems="stretch" spacing="2">
              {navItems.map(item => (
                <NavButton key={item.to} item={item} onClick={onClose} />
              ))}
              {authUser ? (
                <Button
                  colorScheme="teal"
                  leftIcon={<FiLogOut />}
                  mt="4"
                  onClick={handleLogout}
                  variant="outline"
                >
                  Logout
                </Button>
              ) : (
                <Button
                  as={RouterLink}
                  to="/login"
                  colorScheme="teal"
                  mt="4"
                  onClick={onClose}
                  variant="outline"
                >
                  Login
                </Button>
              )}
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default Header;
