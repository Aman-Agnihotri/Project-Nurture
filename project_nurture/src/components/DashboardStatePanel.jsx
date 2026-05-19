import {
  Alert,
  AlertIcon,
  Box,
  Code,
  Heading,
  HStack,
  Spinner,
  Text,
  VStack,
} from '@chakra-ui/react';
import PropTypes from 'prop-types';
import { FiDatabase } from 'react-icons/fi';

const stateContent = {
  loading: {
    title: 'Loading DHS Dashboard Extract',
    body: 'Reading the generated local extract before drawing the map and indicators.',
    tone: 'info',
  },
  missing: {
    title: 'DHS Extract Not Generated',
    body: 'The dashboard needs a local JSON extract built from approved DHS files before it can render.',
    tone: 'warning',
  },
  empty: {
    title: 'Generated Extract Has No Mapped Rows',
    body: 'The app found the generated file, but it does not contain usable mapped child nutrition rows.',
    tone: 'warning',
  },
};

const DashboardStatePanel = ({ status }) => {
  const content = stateContent[status] || stateContent.loading;
  const isLoading = status === 'loading';

  return (
    <Box
      bg="white"
      borderColor="blackAlpha.200"
      borderRadius="md"
      borderWidth="1px"
      boxShadow="0 14px 34px rgba(15, 23, 42, 0.08)"
      p={['5', '6']}
    >
      <VStack alignItems="flex-start" spacing="4">
        <HStack spacing="3">
          {isLoading ? <Spinner color="teal.500" /> : <FiDatabase color="#0f766e" size="22" />}
          <Heading size="md">{content.title}</Heading>
        </HStack>
        <Text color="gray.600" maxW="760px">
          {content.body}
        </Text>
        {!isLoading && (
          <Alert status={content.tone} borderRadius="md" alignItems="flex-start">
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold">Regenerate the local dashboard data</Text>
              <Text fontSize="sm" color="gray.700" mt="1">
                Run <Code>python python_backend/dhs_pipeline.py</Code> after placing the required
                DHS files under <Code>dhs_data</Code>. The generated JSON should stay local because
                it is derived from restricted DHS microdata.
              </Text>
            </Box>
          </Alert>
        )}
      </VStack>
    </Box>
  );
};

DashboardStatePanel.propTypes = {
  status: PropTypes.oneOf(['loading', 'missing', 'empty']).isRequired,
};

export default DashboardStatePanel;
