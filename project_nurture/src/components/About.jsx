import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Box,
} from '@chakra-ui/react';

const About = () => {
  return (

      <Box textAlign={"center"} justifyContent={"center"}
      p={"100px"}
      >
        <Accordion allowToggle allowMultiple>
          <AccordionItem>
            <h2>
            <AccordionButton _expanded={{ bg: 'teal', color: 'white' }}>
                <Box as="span" flex='1' textAlign='left'>
                  AMAN AGNIHOTRI
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
             PreFinal Year Student of UPES.
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
            <AccordionButton _expanded={{ bg: 'teal', color: 'white' }}>
                <Box as="span" flex='1' textAlign='left'>
                PRANNTI AGNIHOTRI
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
            PreFinal Year Student of UPES.
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
            <AccordionButton _expanded={{ bg: 'teal', color: 'white' }}>
                <Box as="span" flex='1' textAlign='left'>
                SHIVAM KUMAR
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
            PreFinal Year Student of UPES.
            </AccordionPanel>
          </AccordionItem>

          <AccordionItem>
            <h2>
              <AccordionButton _expanded={{ bg: 'teal', color: 'white' }}>
                <Box as="span" flex='1' textAlign='left'>
                  SACHIN AGGARWAL
                </Box>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            <AccordionPanel pb={4}>
            PreFinal Year Student of UPES.
            </AccordionPanel>
          </AccordionItem>
        </Accordion>
      </Box>
  );
};

export default About;
