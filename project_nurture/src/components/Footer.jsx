import { Box, Button, HStack, Heading, Input, Stack, VStack, Text } from '@chakra-ui/react';
import {AiOutlineSend,AiOutlineInstagram,AiFillLinkedin,AiFillGithub } from 'react-icons/ai'

const Footer = () => {
  return (
   <Box bgColor={"blackAlpha.100"} minH={'40'} p='16'>


<Stack direction={['column','row']} >

<VStack alignItems={"stretch"} w={"full"} px={"4"}>
   
    <Heading 
    color={'blue.600'} size={"lg"} textTransform={"uppercase"} textAlign={["center",'left']} 
    > CONTACT US
    </Heading>

    <HStack 
    borderBottom={"2px solid teal"} py='2' 
    >
        <Input color={'blue.600'} placeholder='enter your email' border={"none"} borderRadius={"none"} outline={"none"} 
    />

        <Button p={"0"} colorScheme={"teal"} variant={"ghost"}  borderRadius={"0 20px 20px 0"}>
            <AiOutlineSend  size={"24"}/>
        </Button>

    </HStack>
</VStack>

<VStack w={"full"} 
borderLeft={['none','2px solid teal']} 
borderRight={['none','2px solid teal']}>
    <Heading color={'blue.600'} textTransform={"uppercase"}
    size='lg' textAlign={"center"} >MALNUTRITION WATCH</Heading>
    <Text size='lg' color={'blue.600'}>@All Rights Reserved</Text>
</VStack>

<VStack w={"full"}  >

    <Heading 
      color={'blue.600'} 
      textTransform={"uppercase"}
      size={"md"} 
      >
      Social Media
    </Heading>

    <Button color={'red.300'} variant={"link"} colorScheme={"white"}>
        <a href='https://www.instagram.com/sach_18_in/' target={'blank'}><AiOutlineInstagram size={"24"} /></a>
    </Button>

    <Button color={'blue.500'} variant={"link"} py='2' colorScheme={"white"}>
        <a href='https://www.linkedin.com/in/sachin-aggarwal-32b162227/' target={'blank'}><AiFillLinkedin size={"24"} /></a>
    </Button>
    
    <Button color={'linkedin'} variant={"link"} colorScheme={"white"}>
        <a href='https://github.com/sachinaggarwal18' target={'blank'}><AiFillGithub size={"24"} /></a>
    </Button>

</VStack>



</Stack>

   </Box>
  )
}

export default Footer