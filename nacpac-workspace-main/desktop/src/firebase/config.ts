// ─────────────────────────────────────────────────────────────────
//  NACPAC Desktop — Firebase Config
//  Copy your Firebase credentials from the Firebase Console here.
//  See shared/firebaseConfig.template.ts for instructions.
// ─────────────────────────────────────────────────────────────────
import { initializeApp, getApps } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
 apiKey: "AIzaSyAmvqkpyBKEZogyk0j_Ti9ob6eUntE2CeM",
  authDomain: "nacpac-production-4134a.firebaseapp.com",
  projectId: "nacpac-production-4134a",
  storageBucket: "nacpac-production-4134a.firebasestorage.app",
  messagingSenderId: "371880247454",
  appId: "1:371880247454:web:b9ae971b4aa16bea673b8f"
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const auth    = getAuth(app);
export const db      = getFirestore(app);
export const storage = getStorage(app);

export default app;
