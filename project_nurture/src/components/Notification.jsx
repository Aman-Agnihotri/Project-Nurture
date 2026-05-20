import { useColorMode } from '@chakra-ui/react';
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Notification = () => {
  const { colorMode } = useColorMode();

  return (
    <div className=''>
      <ToastContainer position="bottom-right" theme={colorMode} />
    </div>
  )
}

export default Notification
