import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";


const firebaseConfig = {
  apiKey: "AIzaSyDBNfAChYc32gfd9i-FqWQTruK1iMZi1QQ",
  authDomain: "groovy-app-b70e4.firebaseapp.com",
  projectId: "groovy-app-b70e4",
  storageBucket: "groovy-app-b70e4.appspot.com",
  messagingSenderId: "8021360748",
  appId: "1:8021360748:web:8cb949457343db0d749849"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);


export const auth = getAuth(app);         // For login/signup
export const db = getFirestore(app);      // For saving user data
export default app;
