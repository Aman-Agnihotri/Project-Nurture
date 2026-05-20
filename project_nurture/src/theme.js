import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  semanticTokens: {
    colors: {
      'app.bg': {
        default: 'gray.50',
        _dark: 'gray.900',
      },
      'app.surface': {
        default: 'white',
        _dark: 'gray.800',
      },
      'app.surfaceMuted': {
        default: 'gray.50',
        _dark: 'gray.700',
      },
      'app.border': {
        default: 'blackAlpha.100',
        _dark: 'whiteAlpha.200',
      },
      'app.borderStrong': {
        default: 'blackAlpha.200',
        _dark: 'whiteAlpha.300',
      },
      'app.heading': {
        default: 'gray.900',
        _dark: 'gray.50',
      },
      'app.text': {
        default: 'gray.800',
        _dark: 'gray.100',
      },
      'app.muted': {
        default: 'gray.600',
        _dark: 'gray.300',
      },
      'app.subtle': {
        default: 'gray.500',
        _dark: 'gray.400',
      },
      'app.brand': {
        default: 'teal.700',
        _dark: 'teal.200',
      },
      'app.icon': {
        default: 'teal.700',
        _dark: 'teal.300',
      },
      'app.headerBg': {
        default: 'rgba(255, 255, 255, 0.95)',
        _dark: 'rgba(17, 24, 39, 0.94)',
      },
    },
  },
  styles: {
    global: {
      body: {
        bg: 'app.bg',
        color: 'app.text',
      },
    },
  },
});

export default theme;
