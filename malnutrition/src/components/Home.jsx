import { Box, Container, Heading, Image } from '@chakra-ui/react';
import React from 'react';
import { Carousel } from 'react-responsive-carousel';
import 'react-responsive-carousel/lib/styles/carousel.min.css';

import img1 from '../assets/img1.webp';
import img2 from '../assets/img2.png';
import img3 from '../assets/img3.webp';
import img4 from '../assets/logo.jpeg';

const headingOptions={

  pos:"absolute",
  left:"50%",
  top:"35%",
  transform:"translate(-50%,-50%)",
  textTransform:"uppercase",
  p:'4'
}

const Home = () => {
  return (
     <Box >
 {/* w="80%" margin="0 auto" */}
      <MyCarousel />

        <Container
          maxW={'container.xl'} maxH={'100vh'} p='16' 
        >
          <Heading 
           textTransform={"uppercase"} 
           py='2' w="fit-content" 
           borderBottom={'2px solid teal'}
           m='auto' fontSize='2xl'
          >
            "Experience the transformative power of our platform as we work together to end childhood malnutrition. With your support, we can create a world where every child has access to the nourishment they need to live healthy, vibrant lives."
            </Heading>
        </Container>

      </Box>
  );
};

const MyCarousel = () => (
  <Carousel 
    autoPlay={true}
    infiniteLoop
    interval={1000}
    showStatus={false}
    showThumbs={false}
    >
      
    <Box w="full" h={'100vh'}>
      <Image src={img4} h="full" w={['full','50%']}  objectFit={'cover'} />
      <Heading bgColor={'blackAlpha.700'} color={'white'} fontSize="30px" {...headingOptions}>
        "Welcome"
      </Heading>
    </Box>

    <Box w="full" h={'100vh'}>
      <Image src={img1} h="full" w={['full','50%']}  objectFit={'cover'} />
      <Heading bgColor={'blackAlpha.400'} color={'white'} {...headingOptions}>
      "Empty Bowl, Full Heart: A Cry for Compassion"
      </Heading>
    </Box>

    <Box w="full" h={'100vh'}>
      <Image src={img2} h="full" w={'full'} objectFit={'cover'} />
      <Heading bgColor={'blackAlpha.500'} color={'white'} {...headingOptions}>
      "Nutrient Deficiency Impacting Child Growth"
      </Heading>

    </Box>

    <Box w="full" h={'100vh'}>
      <Image src={img3} h="full" w={'full'} objectFit={'cover'} />
      <Heading bgColor={'whiteAlpha.700'} color={'black'} {...headingOptions}>
      "Unequal Childhoods: From Screens to Empty Stomachs"
      </Heading>
      <Heading>POWER</Heading>
    </Box>
  </Carousel>
);

export default Home;