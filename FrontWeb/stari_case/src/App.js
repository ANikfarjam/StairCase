import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './CommonComponents/nav_bar';
import LandingPage from './CommonComponents/landing_page'; // make sure the path is correct

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* Add About, Login, Signup routes here */}
      </Routes>
    </Router>
  );
}

export default App;
