// ─────────────────────────────────────────────────────────────────
//  NACPAC Firebase Configuration Template
//
//  INSTRUCTIONS:
//  1. Go to https://console.firebase.google.com
//  2. Create a new project named "nacpac-production"
//  3. Enable: Authentication → Email/Password
//  4. Enable: Firestore Database (start in production mode)
//  5. Enable: Storage
//  6. Project Settings → Add App → Web → copy config below
//  7. Copy this file to both:
//       mobile/firebase/config.ts
//       desktop/src/firebase/config.ts
//  8. Replace all placeholder values with your real Firebase config
// ─────────────────────────────────────────────────────────────────

export const firebaseConfig = {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT_ID.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId:             "YOUR_APP_ID",
};
