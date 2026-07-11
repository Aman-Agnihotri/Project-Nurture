/**
 * Non-dismissable info banner shown only when the dashboard is rendering Tier 2 (demo) data,
 * to make clear the map and indicators reflect synthetic demonstration data rather than the
 * restricted-local DHS extract.
 */
import { Alert, AlertDescription, AlertIcon } from '@chakra-ui/react';
import PropTypes from 'prop-types';

const DEFAULT_MESSAGE =
  'Synthetic demonstration data derived from published NFHS-5 district fact sheets. Cluster locations are randomly generated and do not represent real survey clusters.';

const DemoBanner = ({ message = DEFAULT_MESSAGE }) => (
  <Alert status="info" borderRadius="md" py="2" mb="4" alignItems="flex-start">
    <AlertIcon />
    <AlertDescription fontSize="sm" whiteSpace={['normal', 'normal', 'nowrap']}>
      {message}
    </AlertDescription>
  </Alert>
);

DemoBanner.propTypes = {
  message: PropTypes.string,
};

export default DemoBanner;
