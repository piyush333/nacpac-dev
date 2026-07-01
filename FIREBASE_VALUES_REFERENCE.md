# Firebase Configuration Values - Ready to Deploy

This file contains the Firebase values needed for Oracle Cloud deployment.
Copy these into your `~/.env` file on the Oracle instance.

## Firebase Configuration (Complete)

```bash
FIREBASE_API_KEY=AIzaSyAmvqkpyBKEZogyk0j_Ti9ob6eUntE2CeM
FIREBASE_AUTH_DOMAIN=nacpac-production-4134a.firebaseapp.com
FIREBASE_PROJECT_ID=nacpac-production-4134a
FIREBASE_STORAGE_BUCKET=nacpac-production-4134a.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=371880247454
FIREBASE_APP_ID=1:371880247454:web:b9ae971b4aa16bea673b8f
```

## How to Use

1. On Oracle Cloud instance, open the template:
   ```bash
   nano ~/.env
   ```

2. Find the Firebase section (lines 56-63)

3. Replace these placeholders:
   ```
   FIREBASE_API_KEY=<PASTE_FIREBASE_API_KEY>
   FIREBASE_AUTH_DOMAIN=<PASTE_FIREBASE_AUTH_DOMAIN>
   FIREBASE_STORAGE_BUCKET=<PASTE_FIREBASE_STORAGE_BUCKET>
   FIREBASE_MESSAGING_SENDER_ID=<PASTE_FIREBASE_MESSAGING_SENDER_ID>
   FIREBASE_APP_ID=<PASTE_FIREBASE_APP_ID>
   ```

4. With the values above

5. Save (Ctrl+X, then Y, then Enter in nano)

6. Verify:
   ```bash
   grep FIREBASE ~/.env
   ```

---

**Status:** All 44 credentials ready for deployment ✅
