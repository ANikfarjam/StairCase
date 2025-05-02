import React from 'react';
import landingImage from '../Assets/landingpage_image.png';
import logo from '../Assets/logo.jpeg';
import { Link } from 'react-router-dom';
import './styling/landing_page.css';

const LandingPage = () => {
  return (
    <div className="landing-container">
      <section className="landing-hero">
        <h1 className="landing-title">
          Welcome to <span className="landing-highlight">StairCase</span>
        </h1>
        <p className="landing-subtext">
          A modern twist on the classic Snakes & Ladders board game, now with interactive mini challenges such as Hangman and Trivia Games powered by our LangChain Agnets and utilizing Llama 2.3 Large Language Model(meta)!
        </p>
        <Link to="/login" className="landing-button">Start Playing</Link>
      </section>

      <section className="combined-banner">
        <div className="image-with-logo">
          <img src={landingImage} alt="StairCase game" className="banner-image" />
          <img src={logo} alt="StairCase logo" className="banner-logo" />
        </div>
      </section>
      <section className="game-review-section">
        <p className="landing-subtext2">
            We developed this game for PC and Mac to help people reconnect and relive the joy of playing together.
            The game supports up to 2 players, taking turns to roll a dice and move 1–6 spaces forward. 
            The board, an NxN grid, includes ladders to help players advance and snakes to pull them back.
        </p>
      </section>
    </div>
  );
};

export default LandingPage;
