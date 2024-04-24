import { BrowserRouter as Router,Route,Routes } from 'react-router-dom';
import Header from "./components/Header";
import Home from "./components/Home";
import Footer from './components/Footer';
import Login from './components/Login';
import Signup from './components/Signup.jsx';
import About from './components/About.jsx';
import Form from './components/Form.jsx';
import Dashboard from './components/Dashboard.jsx';

function App() {
  return (
    <Router>
     <Header/>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/form" element={<Form />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/about" element={<About />} />
    </Routes>
      <Footer/>
    </Router>
  );
}

export default App;