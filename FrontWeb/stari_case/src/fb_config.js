// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from 'firebase/auth';
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional

const firebaseConfig = {
  apiKey: process.env.REACT_APP_API_KEY,
  authDomain: process.env.REACT_APP_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_PROJECT_ID,
  storageBucket: process.env.REACT_APP_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_APP_ID,
  measurementId: process.env.REACT_APP_MEASUREMENT_ID
};
// const firebaseConfig = {
//   apiKey: "AIzaSyDD3xzq6p9yVDIW2l4LvpEJPzDfUTq8jPY",
//   authDomain: "staircase-b37df.firebaseapp.com",
//   projectId: "staircase-b37df",
//   storageBucket: "staircase-b37df.appspot.com",   // <-- Make sure this is correct
//   messagingSenderId: "1034412560246",
//   appId: "1:1034412560246:web:11c29b654d396b360bf457",
//   measurementId: "G-NBP8SRFBQ4"
// };

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app)
const analytics = getAnalytics(app)
const db = getFirestore(app)
export{app, auth, analytics, db}