import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './CommonComponents/nav_bar';
import LandingPage from './CommonComponents/landing_page'; // make sure the path is correct
import LoginPage from './CommonComponents/log_in';
import SignUpPage from './CommonComponents/sign_up';
import Dashboard from './CommonComponents/dashboard';
import AboutPage from './CommonComponents/about';
function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage/>}/>
        <Route path="/about" element={<AboutPage/>}/>
        <Route path="/signup" element={<SignUpPage/>}/>
        <Route path="/dashboard" element={<Dashboard/>}/>
        {/* Add About, Login, Signup routes here */}
      </Routes>
    </Router>
  );
}

export default App;
