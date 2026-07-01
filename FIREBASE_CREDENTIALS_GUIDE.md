# How to Find Firebase API Key & Auth Domain

## Quick Summary
You need to find **5 Firebase config values**. Here's the easiest way:

---

## Method 1: Firebase Console Web App Config (EASIEST) ⭐

### Step 1: Go to Firebase Console
Open: **https://console.firebase.google.com/**

### Step 2: Select Your Project
- Click on project: **nacpac-production-4134a**
- (You should see it in your projects list)

### Step 3: Find Web App Settings
1. In left sidebar, click **Project Settings** (⚙️ gear icon at bottom)
2. Scroll down to section: **"Your apps"**
3. Look for a web app with icon **</> (code brackets)**
4. If no web app exists, click **"Add app"** → select **Web** → register

### Step 4: Copy Config Object
You'll see a code block like:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "nacpac-production-4134a.firebaseapp.com",
  projectId: "nacpac-production-4134a",
  storageBucket: "nacpac-production-4134a.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123xyz789abc"
};
```

### Step 5: Extract These 5 Values

| Key | Value | Where to Paste |
|-----|-------|-----------------|
| **apiKey** | AIzaSy... | `FIREBASE_API_KEY=` |
| **authDomain** | nacpac-production-4134a.firebaseapp.com | `FIREBASE_AUTH_DOMAIN=` |
| **storageBucket** | nacpac-production-4134a.appspot.com | `FIREBASE_STORAGE_BUCKET=` |
| **messagingSenderId** | 123456789012 | `FIREBASE_MESSAGING_SENDER_ID=` |
| **appId** | 1:123456789012:web:abc123xyz789abc | `FIREBASE_APP_ID=` |

---

## Method 2: If You Already Have google-services.json

If you have the file from mobile app:

### Mobile: `google-services.json`
Location: `nacpac-workspace-main/mobile/google-services.json`

Look for this section:
```json
{
  "project_info": {
    "project_id": "nacpac-production-4134a"
  },
  "client": [
    {
      "client_info": {
        "mobilesdk_app_id": "1:123456789012:android:abc..."
      }
    }
  ]
}
```

This has different format but you can use it to verify project ID.

### Desktop: Firebase config in code
Location: `nacpac-workspace-main/desktop/src/firebase/config.ts`

Should already have the values in comments or config.

---

## Method 3: Visual Step-by-Step (Screenshots)

### Screenshot 1: Firebase Console Home
```
https://console.firebase.google.com/
↓
[See list of projects]
↓
Click: nacpac-production-4134a
```

### Screenshot 2: Project Settings
```
[Inside nacpac-production-4134a project]
↓
Bottom left: ⚙️ Settings icon
↓
Click: Project Settings
```

### Screenshot 3: Find Web App
```
[Project Settings page]
↓
Scroll down to: "Your apps"
↓
Look for: </> Web App
↓
If not there → Click "Add app" → Web
```

### Screenshot 4: Config Code
```
[Web App section]
↓
You'll see a code block starting with:
const firebaseConfig = {
  apiKey: "...",
  authDomain: "...",
  ...
}
```

Copy the entire object inside the braces `{...}`

---

## Copy-Paste Format

Once you have the 5 values, provide them like this:

```
FIREBASE_API_KEY=AIzaSy_YourActualKeyHere
FIREBASE_AUTH_DOMAIN=nacpac-production-4134a.firebaseapp.com
FIREBASE_STORAGE_BUCKET=nacpac-production-4134a.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789012
FIREBASE_APP_ID=1:123456789012:web:abc123xyz789abc
```

---

## Troubleshooting

### "I don't see a web app"
→ Click **"Add app"** in the "Your apps" section
→ Select **Web** (</> icon)
→ Give it a name (e.g., "Discord Bot")
→ Register
→ Copy the config

### "I see Android/iOS but not Web"
→ Scroll down further in "Your apps"
→ Or click **"Add app"** to create web config
→ The web config has the apiKey and authDomain you need

### "authDomain looks wrong"
→ It should be: `nacpac-production-4134a.firebaseapp.com`
→ NOT: `nacpac-production-4134a.web.app` (that's for hosting)

### "I can't access Firebase Console"
→ Make sure you're logged in with: **piyushjindal333@gmail.com**
→ Go to: https://console.firebase.google.com/
→ Check if you have access to the project
→ Contact Firebase support if access is denied

---

## Quick Reference: What Each Value Is

| Field | Example | Purpose |
|-------|---------|---------|
| **apiKey** | `AIzaSy_...` | Identifies your app to Firebase (public, safe to expose) |
| **authDomain** | `nacpac-production-4134a.firebaseapp.com` | Used for authentication redirects |
| **projectId** | `nacpac-production-4134a` | Your Firebase project ID (already known) |
| **storageBucket** | `nacpac-production-4134a.appspot.com` | Cloud Storage bucket for files |
| **messagingSenderId** | `123456789012` | For Firebase Cloud Messaging (notifications) |
| **appId** | `1:123456789012:web:abc...` | Unique app identifier |

---

## After Getting Values

1. Copy the 5 values above
2. Paste them in this message format:
   ```
   FIREBASE_API_KEY=<your_api_key>
   FIREBASE_AUTH_DOMAIN=<your_auth_domain>
   FIREBASE_STORAGE_BUCKET=<your_storage_bucket>
   FIREBASE_MESSAGING_SENDER_ID=<your_messaging_sender_id>
   FIREBASE_APP_ID=<your_app_id>
   ```

3. Send them to me → I'll complete the deployment

**Est. time:** 2-3 minutes to find and copy values

---

## Direct Links

- **Firebase Console:** https://console.firebase.google.com/
- **Your Project:** https://console.firebase.google.com/project/nacpac-production-4134a/settings/general
- **Web App Config:** https://console.firebase.google.com/project/nacpac-production-4134a/settings/general (scroll to "Your apps")
