import {
  Alert,
  AlertIcon,
  Badge,
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  Input,
  Select,
  SimpleGrid,
  Stack,
  Text,
  Textarea,
  VStack,
} from '@chakra-ui/react';
import { useState } from 'react';
import { toast } from 'react-toastify';

const initialFormData = {
  childId: '',
  guardianName: '',
  ageMonths: '',
  sex: '',
  state: '',
  district: '',
  heightCm: '',
  weightKg: '',
  muacCm: '',
  followUpStatus: 'new',
  notes: '',
};

const statusOptions = [
  { label: 'New case', value: 'new' },
  { label: 'Follow-up due', value: 'follow-up' },
  { label: 'Improving', value: 'improving' },
  { label: 'Escalate', value: 'escalate' },
];

const Form = () => {
  const [formData, setFormData] = useState(initialFormData);
  const [draftSaved, setDraftSaved] = useState(false);

  const handleChange = event => {
    const { name, value } = event.target;
    setDraftSaved(false);
    setFormData(current => ({
      ...current,
      [name]: value,
    }));
  };

  const handleSubmit = event => {
    event.preventDefault();
    setDraftSaved(true);
    toast.info('Private workflow draft captured locally for this session only.', {
      position: 'bottom-right',
      autoClose: 4000,
    });
  };

  const resetForm = () => {
    setFormData(initialFormData);
    setDraftSaved(false);
  };

  return (
    <Box bg="app.bg" minH="calc(100vh - 64px)" py={['10', '14']}>
      <Container maxW="container.xl" px={['4', '6', '8']}>
        <Stack direction={['column', 'column', 'row']} spacing="8" alignItems="flex-start">
          <Box flex="0.95" maxW={['full', 'full', '420px']}>
            <Badge colorScheme="teal" mb="4">
              Future private workflow
            </Badge>
            <Heading color="app.heading" size="xl">
              Child Follow-up Workflow
            </Heading>
            <Text color="app.muted" mt="4">
              This screen frames the secure operational layer Project Nurture could support
              later: collecting field observations, tracking follow-up status, and linking
              local case work back to broader dashboard insights.
            </Text>
            <Alert status="info" borderRadius="md" mt="6" alignItems="flex-start">
              <AlertIcon />
              <Box>
                <Text fontWeight="semibold">No records are stored yet.</Text>
                <Text fontSize="sm">
                  This public portfolio version does not write child case details to a database.
                  A real deployment would need consent, access control, audit logs, and a secure backend.
                </Text>
              </Box>
            </Alert>
          </Box>

          <Box
            as="form"
            bg="app.surface"
            borderColor="app.border"
            borderRadius="md"
            borderWidth="1px"
            boxShadow="0 16px 36px rgba(15, 23, 42, 0.08)"
            flex="1.4"
            onSubmit={handleSubmit}
            p={['5', '6']}
            w="full"
          >
            <VStack alignItems="stretch" spacing="6">
              <Box>
                <Heading size="md">Child Follow-up Draft</Heading>
                <Text color="app.muted" fontSize="sm" mt="1">
                  Capture a minimal, reviewable case snapshot for future private workflows.
                </Text>
              </Box>

              <SimpleGrid columns={[1, 2]} spacing="4">
                <FormControl isRequired>
                  <FormLabel>Child or case ID</FormLabel>
                  <Input
                    name="childId"
                    onChange={handleChange}
                    placeholder="PN-CASE-001"
                    value={formData.childId}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Guardian name</FormLabel>
                  <Input
                    name="guardianName"
                    onChange={handleChange}
                    placeholder="Optional"
                    value={formData.guardianName}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Age in months</FormLabel>
                  <Input
                    min="0"
                    max="59"
                    name="ageMonths"
                    onChange={handleChange}
                    placeholder="0-59"
                    type="number"
                    value={formData.ageMonths}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Sex</FormLabel>
                  <Select name="sex" onChange={handleChange} value={formData.sex}>
                    <option value="">Select</option>
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>State / UT</FormLabel>
                  <Input
                    name="state"
                    onChange={handleChange}
                    placeholder="State or union territory"
                    value={formData.state}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>District</FormLabel>
                  <Input
                    name="district"
                    onChange={handleChange}
                    placeholder="District"
                    value={formData.district}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Height (cm)</FormLabel>
                  <Input
                    min="0"
                    name="heightCm"
                    onChange={handleChange}
                    placeholder="Optional"
                    step="0.1"
                    type="number"
                    value={formData.heightCm}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Weight (kg)</FormLabel>
                  <Input
                    min="0"
                    name="weightKg"
                    onChange={handleChange}
                    placeholder="Optional"
                    step="0.1"
                    type="number"
                    value={formData.weightKg}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>MUAC (cm)</FormLabel>
                  <Input
                    min="0"
                    name="muacCm"
                    onChange={handleChange}
                    placeholder="Optional"
                    step="0.1"
                    type="number"
                    value={formData.muacCm}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Follow-up status</FormLabel>
                  <Select
                    name="followUpStatus"
                    onChange={handleChange}
                    value={formData.followUpStatus}
                  >
                    {statusOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </SimpleGrid>

              <FormControl>
                <FormLabel>Visit notes</FormLabel>
                <Textarea
                  name="notes"
                  onChange={handleChange}
                  placeholder="Observations, referral notes, caregiver context, or next visit plan"
                  resize="vertical"
                  rows={4}
                  value={formData.notes}
                />
              </FormControl>

              {draftSaved && (
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  Draft captured locally. This public version does not persist or transmit records.
                </Alert>
              )}

              <HStack justifyContent="flex-end" flexWrap="wrap" spacing="3">
                <Button onClick={resetForm} variant="outline" w={['full', 'auto']}>
                  Clear
                </Button>
                <Button colorScheme="teal" type="submit" w={['full', 'auto']}>
                  Review Draft
                </Button>
              </HStack>
            </VStack>
          </Box>
        </Stack>
      </Container>
    </Box>
  );
};

export default Form;
