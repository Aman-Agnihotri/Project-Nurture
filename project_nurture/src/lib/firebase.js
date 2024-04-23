import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyB7eTdjoIfAUTO4pBTjhCj0Np2h3bqPpJA",
  authDomain: "project-nurture.firebaseapp.com",
  projectId: "project-nurture",
  storageBucket: "project-nurture.appspot.com",
  messagingSenderId: "972337939607",
  appId: "1:972337939607:web:afd880c4f21803ce0cd5d2"
};

// Initialize Firebase
initializeApp(firebaseConfig);

export const auth = getAuth()
export const db = getFirestore()