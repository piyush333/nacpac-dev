import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY || "AIzaSyDummy_Replace_With_Real_Key",
  authDomain: "nacpac-production-4134a.firebaseapp.com",
  projectId: "nacpac-production-4134a",
  storageBucket: "nacpac-production-4134a.appspot.com",
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "0",
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID || "1:0:web:0",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
