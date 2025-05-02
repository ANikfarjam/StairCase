import React, { useEffect, useRef, useState } from 'react';
import './styling/sign_up.css';
import { auth, db } from '../fb_config';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { doc, setDoc } from 'firebase/firestore';
import { useNavigate } from 'react-router-dom';

const SignUpPage = () => {
  const canvasRef = useRef();
  const navigate = useNavigate()
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const themeColors = ['#6A0DAD', '#FF6B81', '#FFA07A', '#FFD1DC', '#C084FC', '#FFB347', '#F472B6', '#D8B4FE'];
    const particles = Array.from({ length: 120 }).map(() => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      radius: Math.random() * 8 + 3,
      dx: (Math.random() - 0.5) * 0.8,
      dy: (Math.random() - 0.5) * 0.8,
      color: themeColors[Math.floor(Math.random() * themeColors.length)],
    }));

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(p => {
        p.x += p.dx;
        p.y += p.dy;
        if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.fill();
      });
      requestAnimationFrame(animate);
    };
    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    const { fullName, email, password, confirmPassword } = form;
  
    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }
  
    if (!fullName.trim()) {
      return setError('Username cannot be empty');
    }
  
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
  
      await setDoc(doc(db, 'Users', user.uid), {
        Username: fullName,
        email: email,
        NumberOfWins: 0,
        Points: 100,
        FriendsList: []
      });
  
      alert('Account created successfully!');
      navigate('/dashboard');
    } catch (err) {
      console.error("Firebase Error:", err.code, err.message);
      setError(err.message || "Signup failed. Please try again.");
    }
  };  
  
  

  return (
    <div className="signup-wrapper">
      <canvas ref={canvasRef} className="signup-canvas" />
      <div className="signup-box">
        <h2>Create an Account</h2>
        <form onSubmit={handleSubmit}>
          <input type="text" name="fullName" placeholder="User Name" value={form.fullName} onChange={handleChange} required />
          <input type="email" name="email" placeholder="Email" value={form.email} onChange={handleChange} required />
          <input type="password" name="password" placeholder="Password" value={form.password} onChange={handleChange} required />
          <input type="password" name="confirmPassword" placeholder="Confirm Password" value={form.confirmPassword} onChange={handleChange} required />
          <button type="submit">Sign Up</button>
          {error && <p style={{ color: 'red' }}>{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default SignUpPage;
