import React, { useEffect, useState } from 'react';
import { IoLogoWindows } from "react-icons/io";
import { FaAppleWhole } from "react-icons/fa6";
import { auth, db } from '../fb_config';
import { doc, getDoc } from 'firebase/firestore';
import './styling/dashboard.css';

const Dashboard = () => {
  const [userData, setUserData] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      const currentUser = auth.currentUser;
      if (!currentUser) return;

      const userRef = doc(db, 'Users', currentUser.uid);
      const docSnap = await getDoc(userRef);
      if (docSnap.exists()) {
        setUserData(docSnap.data());
      }
    };

    fetchUserData();
  }, []);

  return (
    <div className="dashboard-container">
      <h2>Download Center</h2>
      <div className="card-container">
        <div className="os-card windows">
          <IoLogoWindows className="os-icon" />
          <h3>Windows</h3>
          <p>Download the latest version for Windows.</p>
          <a href="/downloads/app-windows.exe" download className="download-btn">Download</a>
        </div>

        <div className="os-card macos">
          <FaAppleWhole className="os-icon" />
          <h3>macOS</h3>
          <p>Download the latest version for macOS.</p>
          <a href="/downloads/app-mac.dmg" download className="download-btn">Download</a>
        </div>

        {userData && (
          <div className="os-card user">
            <h3>👤 Your Info</h3>
            <p><strong>Username:</strong> {userData.Username}</p>
            <p><strong>Email:</strong> {userData.email}</p>
            <p><strong>Wins:</strong> {userData.NumberOfWins}</p>
            <p><strong>Points:</strong> {userData.Points}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
