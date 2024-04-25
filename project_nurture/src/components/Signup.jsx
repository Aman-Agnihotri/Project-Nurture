import {
  Avatar,
  Button,
  Container,
  Heading,
  Input,
  Text,
  VStack,
} from '@chakra-ui/react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from "react-toastify";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth, db } from "../lib/firebase";
// import { collection, query, where, doc, setDoc, getDocs } from "firebase/firestore";
import { doc, setDoc } from "firebase/firestore";

const Signup = () => {
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const { username, email, password } = Object.fromEntries(formData);

    // // VALIDATE INPUTS
    // if (!username || !email || !password)
    //   return toast.warn("Please enter inputs!");

    // // VALIDATE UNIQUE USERNAME
    // const usersRef = collection(db, "users");
    // const q = query(usersRef, where("username", "==", username));
    // const querySnapshot = await getDocs(q);
    // if (!querySnapshot.empty) {
    //   return toast.warn("Select another username");
    // }

    try {
      const res = await createUserWithEmailAndPassword(auth, email, password);

      await setDoc(doc(db, "users", res.user.uid), {
        username,
        email,
        id: res.user.uid,
        blocked: [],
      });

      toast.success('Account created!', {
        position: "bottom-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
      navigate('/login');
    } catch (err) {
      console.log(err);

      toast.error('Signup failed: ' + err.message, {
        position: "bottom-right",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    }
   
  };

  return (
    <Container maxW={'container.xl'} h={'100vh'} p={'16'}>
      <form onSubmit={handleRegister}>
        <VStack
          alignItems={'stretch'}
          spacing={'8'}
          w={['full', '96']}
          m={'auto'}
          my={'16'}
        >
          <Heading
          lineHeight={"38px"}
          >MAKE AN ACCOUNT TO ACCESS MAP</Heading>
          <Avatar alignSelf={'center'} boxSize={'32'} />

          <Input
            placeholder={'Name'}
            type={'text'}
            required = {true}
            focusBorderColor={' teal.500'}
            name = {"username"}
          />
          <Input
            placeholder={'Email'}
            type={'text'}
            required = {true}
            focusBorderColor={' teal.500'}
            name = {"email"}
          />
          <Input
            placeholder={'Password'}
            type={'password'}
            required = {true}
            focusBorderColor={' teal.500'}
            name = {"password"}
          />
          <Text textAlign={'right'}>
              Already Signed Up?{' '}
              <Button variant={'link'} colorScheme={' teal'}>
                <Link to={'/login'}>Login In</Link>
              </Button>
            </Text>
          <Button colorScheme={' teal'} type="submit">Sign Up</Button>
        </VStack>
      </form>
    </Container>
  );
};

export default Signup;
