import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Badge,
  Box,
  Heading,
  HStack,
  Icon,
  SimpleGrid,
  Text,
} from '@chakra-ui/react';
import { FiFilter, FiInfo, FiMap, FiShield, FiTarget } from 'react-icons/fi';

const guideItems = [
  {
    icon: FiInfo,
    title: 'What this dashboard is',
    text: 'A local explorer for India Standard DHS 2019-21 child nutrition indicators. It is meant for aggregate insight and planning-style analysis.',
  },
  {
    icon: FiMap,
    title: 'How to read the map',
    text: 'Colors represent the selected indicator. Cluster bubbles show weighted averages across visible DHS survey clusters. Heat is optional and smoothed, not exact case geography.',
  },
  {
    icon: FiFilter,
    title: 'What filters do',
    text: 'Filters rebuild the mapped aggregate from DHS child records by state, district, residence, sex, wealth, and child age band.',
  },
  {
    icon: FiTarget,
    title: 'Why priority areas exist',
    text: 'Priority areas combine indicator severity with mapped sample size so the dashboard can suggest where to inspect first without treating percentages alone as decisions.',
  },
  {
    icon: FiShield,
    title: 'Privacy and limits',
    text: 'DHS GPS points are displaced for confidentiality. The generated JSON comes from restricted microdata and should stay local, not committed or redistributed.',
  },
];

const DashboardGuide = () => {
  return (
    <Accordion allowToggle defaultIndex={[0]} data-tour="dashboard-guide" mb="6">
      <AccordionItem
        bg="app.surface"
        borderColor="app.borderStrong"
        borderRadius="md"
        borderWidth="1px"
      >
        <h2>
          <AccordionButton px="5" py="4">
            <Box flex="1" textAlign="left">
              <HStack spacing="3">
                <Badge colorScheme="teal">Guide</Badge>
                <Heading size="sm">How To Read This Dashboard</Heading>
              </HStack>
              <Text color="app.muted" fontSize="sm" mt="1">
                Data source, map behavior, filters, priority ranking, and privacy limits.
              </Text>
            </Box>
            <AccordionIcon />
          </AccordionButton>
        </h2>
        <AccordionPanel px="5" pb="5">
          <SimpleGrid columns={[1, 1, 2, 5]} spacing="4">
            {guideItems.map(item => (
              <Box key={item.title}>
                <Icon as={item.icon} color="app.icon" boxSize="5" />
                <Heading color="app.text" mt="3" size="xs">
                  {item.title}
                </Heading>
                <Text color="app.muted" fontSize="sm" mt="2">
                  {item.text}
                </Text>
              </Box>
            ))}
          </SimpleGrid>
        </AccordionPanel>
      </AccordionItem>
    </Accordion>
  );
};

export default DashboardGuide;
