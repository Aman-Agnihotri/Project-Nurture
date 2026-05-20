import { ColorModeScript, ChakraProvider } from '@chakra-ui/react';
import { StrictMode } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import theme from './theme';

ReactDOM.createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ColorModeScript initialColorMode={theme.config.initialColorMode} />
    <ChakraProvider theme={theme} >
      <App />
   </ChakraProvider>
  </StrictMode>
)
