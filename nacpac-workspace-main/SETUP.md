# NACPAC Production System — Setup Guide

## System Overview

```
[Android Admin App]  ←──── Firebase ────→  [Windows Operator Dashboard]
     (phone)              (real-time)            (PC at factory)
```

---

## Step 1 — Create Firebase Project

1. Go to **https://console.firebase.google.com**
2. Click **Add project** → name it `nacpac-production`
3. Disable Google Analytics (optional) → Create project

### Enable Authentication
- Left menu → **Authentication** → Get started
- Sign-in method → **Email/Password** → Enable → Save

### Enable Firestore
- Left menu → **Firestore Database** → Create database
- Choose **Production mode** → Select region (asia-south1 for India) → Done

### Enable Storage
- Left menu → **Storage** → Get started
- Accept default rules → Choose same region → Done

### Get Config Credentials
- Project Settings (⚙ gear icon) → General tab → Your apps
- Click **Add app** → Web (</>) → Register app → Copy the `firebaseConfig` object

---

## Step 2 — Add Firebase Credentials to Both Apps

Open these two files and replace ALL `YOUR_*` placeholders with your real values:

```
mobile/firebase/config.ts
desktop/src/firebase/config.ts
```

Paste your Firebase config:
```typescript
const firebaseConfig = {
  apiKey:            "AIzaSy...",
  authDomain:        "nacpac-production.firebaseapp.com",
  projectId:         "nacpac-production",
  storageBucket:     "nacpac-production.appspot.com",
  messagingSenderId: "123456789",
  appId:             "1:123...",
};
```

---

## Step 3 — Deploy Firebase Security Rules

```bash
# Install Firebase CLI (once)
npm install -g firebase-tools

# Login
firebase login

# Initialize (from the nacpac root folder)
firebase init

# Select: Firestore + Storage
# Use existing project: nacpac-production
# Rules files: firebase/firestore.rules and firebase/storage.rules

# Deploy
firebase deploy --only firestore:rules,storage
```

---

## Step 4 — Create User Accounts

Go to Firebase Console → Authentication → Users → Add user

Create two accounts:
| Email                    | Role       | App            |
|--------------------------|------------|----------------|
| admin@nacpac.com         | Admin      | Mobile app     |
| operator@nacpac.com      | Operator   | Windows app    |

---

## Step 5 — Run the Mobile App (Android)

### Prerequisites
- Install **Node.js** 18+ from https://nodejs.org
- Install **Expo Go** from Google Play Store on your Android phone

### Run
```bash
cd mobile
npm install
npx expo start
```

Scan the QR code shown in the terminal with the Expo Go app on your phone.

### Build Android APK (for standalone install)
```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo account (create free at expo.dev)
eas login

# Configure build
eas build:configure

# Build APK
eas build --platform android --profile preview
```

Download the APK from the Expo website and install it on your Android phone.

---

## Step 6 — Run the Windows Operator Dashboard

### Prerequisites
- Install **Node.js** 18+ from https://nodejs.org

### Development mode
```bash
cd desktop
npm install
npm run dev
```

### Build Windows installer (.exe)
```bash
cd desktop
npm run build
```

The installer will be in `desktop/dist/`. Double-click to install on the production PC.

---

## Workflow Guide

### Admin (Phone)
1. Open NACPAC Admin app
2. Sign in with admin account
3. Tap **New Job** tab
4. Fill in:
   - Job title (e.g. "Print 500 flyers — A5")
   - Description / specifications
   - Priority (Urgent / High / Medium / Low)
   - Deadline (optional)
   - Attach PDF files or photos
5. Tap **Send to Production**
6. Job appears instantly on the Windows dashboard

### Operator (Windows)
1. Open NACPAC Production app
2. Sign in with operator account
3. See live job queue — new jobs appear automatically
4. Click a job to open details
5. Download attached files (opens in browser)
6. Add notes in the Operator Notes field
7. Update status:
   - **▶ Start Job** → marks as In Progress (admin sees this)
   - **✔ Complete** → marks as Completed
   - **✕ Reject** → marks as Rejected with reason
8. Admin sees status updates in real-time on their phone

---

## Folder Structure

```
nacpac/
├── shared/                     ← TypeScript types (both apps)
├── mobile/                     ← Android Admin App (Expo)
├── desktop/                    ← Windows Operator App (Electron)
├── firebase/                   ← Firebase security rules
└── SETUP.md                    ← This file
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Firebase connection fails | Check credentials in config.ts files |
| Jobs not appearing in real-time | Check Firestore rules are deployed |
| File upload fails | Check Storage rules are deployed + file < 50MB |
| Expo app crashes | Run `npx expo start --clear` to clear cache |
| Desktop app blank screen | Run `npm run dev` and check webpack console |
