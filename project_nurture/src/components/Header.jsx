import {
  Box,
  Button,
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
import { Link as RouterLink } from 'react-router-dom';
import { FiMenu } from 'react-icons/fi';
import ColorModeSwitcher from '../ColorModeSwitcher';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Explorer', to: '/dashboard' },
  { label: 'Field Intake', to: '/form' },
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

  return (
    <Box
      as="header"
      position="sticky"
      top="0"
      zIndex="sticky"
      borderBottomWidth="1px"
      borderColor="blackAlpha.200"
      bg="rgba(255, 255, 255, 0.95)"
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
                color="teal.700"
                display="block"
                fontSize="lg"
                fontWeight="800"
                lineHeight="1.1"
              >
                Project Nurture
              </Text>
              <Text color="gray.500" fontSize="xs" noOfLines={1}>
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
            <Button
              as={RouterLink}
              to="/dashboard"
              colorScheme="teal"
              display={['none', 'inline-flex']}
              size="sm"
            >
              Open Explorer
            </Button>
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
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader>Project Nurture</DrawerHeader>
          <DrawerBody>
            <VStack alignItems="stretch" spacing="2">
              {navItems.map(item => (
                <NavButton key={item.to} item={item} onClick={onClose} />
              ))}
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
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </Box>
  );
};

export default Header;
