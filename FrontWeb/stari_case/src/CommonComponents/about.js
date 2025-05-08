import React from "react";
import "./styling/about.css";
import about_image from "./about.png";

const AboutPage = () => {
  return (
    <div className="about-container">
      <div className="about-panel">
        <div className="about-text">
          <h1>About <span className="brand-name">StairCase</span></h1>

          <section className="about-section">
            <h2>🎮 Getting Started</h2>
            <p>
              To begin your journey, create an account on our website using your email and a secure username. 
              Once registered, you'll receive access to download the StairCase game client for both Windows and Mac (M-series).
            </p>
            <p>
              After launching the client, log in with your credentials to connect with friends, send game invitations, and start your adventure in multiplayer mode.
            </p>
            <p>
              The game follows a modern twist on a nostalgic classic: roll the dice to advance across a vibrant 10x10 board, dodge snakes, climb ladders, and encounter exciting minigames. Reach tile 100 first to claim victory!
            </p>
          </section>

          <section className="about-section">
            <h2>AI-Powered Minigames</h2>
            <p>
              Some tiles trigger interactive minigames—Trivia and Hangman—designed to test your knowledge and reflexes. 
              Correct answers move you ahead; mistakes pull you back. Powered by AI agents, each challenge offers fresh and engaging content every time you play.
            </p>
          </section>
        </div>

        <div className=" about_image">
          <img src={about_image} alt="Rolling dice by hand" />
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
