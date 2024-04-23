import {
    Drawer,
    DrawerBody,
    DrawerHeader,
    DrawerOverlay,
    DrawerContent,
    DrawerCloseButton,
    Button,useDisclosure,
    VStack, HStack
  } from '@chakra-ui/react'
import {Link} from "react-router-dom"
import {BiMenuAltLeft} from "react-icons/bi"

const Header = () => {
  

const {isOpen, onOpen, onClose} = useDisclosure();
return (
    <>
        <Button
            zIndex={'overlay'}
            position={"fixed"}
            top={'4'}
            left={'4'}
            colorScheme='teal'
            w={"10"}
            h={"10"}
            p={'0'}
            borderRadius={"full"}
            onClick={onOpen}
        >
            <BiMenuAltLeft size={"25"} />
        </Button>

    <Drawer isOpen={isOpen} onClose={onClose} placement='left' >
       <DrawerOverlay/>

        <DrawerContent>
           <DrawerCloseButton />
            <DrawerHeader>
                WELCOME!!
            </DrawerHeader>

            <DrawerBody>
                <VStack
                    alignItems={"flex-start"}
                >

                    <Button variant={"ghost"} colorScheme={"teal"} >
                        <Link to="/" >HOME</Link>
                    </Button>

                    <Button onClick={onClose} variant={'ghost'} colorScheme={'teal'}>
                        <Link to="/about">ABOUT US</Link>
                    </Button>

                    <Button onClick={onClose}  variant={"ghost"} colorScheme={"teal"} >
                        <Link to="/" >FEED</Link>
                    </Button>

                    <Button  onClick={onClose}  variant={"ghost"} colorScheme={"teal"} >
                        <Link to="/" >MORE</Link>
                    </Button>

                    <Button  onClick={onClose}  variant={"ghost"} colorScheme={"teal"} >
                        <Link to="/form" >USER FORM</Link>
                    </Button>

                </VStack>

                <HStack
                    pos={"absolute"} bottom={'10'} left={'0'}  w={"full"}
                    justifyContent={"space-evenly"}
                >

                <Button onClick={onClose} colorScheme={"teal"} >
                        <Link to="/login" >LOGIN</Link>
                </Button>

                <Button onClick={onClose}  variant={"outline"} colorScheme={"teal"} >
                        <Link to="/" >SIGN UP</Link>
                </Button>

                </HStack>

            </DrawerBody>

        </DrawerContent>

    </Drawer>

    </>
  )
}

export default Header