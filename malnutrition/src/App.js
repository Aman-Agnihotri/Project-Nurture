// import { BrowserRouter as Router, Route,Routes } from "react-router-dom";
// import Header from "./components/Header";
// import Home from "./components/Home";
// import About from "./components/About";

// function App() {
//   return (
//     <Router>
//       <Header/>
//       {/* <About/> */}
//       <Routes>
//         <Route  path="/" element={<Home/>} />
//       </Routes>
//     </Router>
//   );
// }

// export default App

import { BrowserRouter as Router,Route,Routes } from 'react-router-dom';
import Header from "./components/Header";
import Home from "./components/Home";
import Footer from './components/Footer';
import Login from './components/Login';
import Signup from './components/Signup.jsx';
import Form from './components/Form.jsx';




function App() {
  return (
    <Router>
     <Header/>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/form" element={<Form />} />
      </Routes>
      <Footer/>
    </Router>
  );
}

export default App;