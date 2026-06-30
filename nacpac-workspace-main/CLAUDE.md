# Nacpac Codebase Map

## Structure
- `mobile/` — Expo React Native app (Android admin app)
  - `mobile/app/` — screens: login.tsx, (tabs)/index.tsx, jobs.tsx, clients.tsx, new-job.tsx, reports.tsx
  - `mobile/components/` — JobCard.tsx
  - `mobile/firebase/` — config.ts, jobs.ts, clients.ts
  - `mobile/shared/types.ts` — shared TypeScript types
- `desktop/` — Electron Windows app (operator production app)
  - `desktop/src/components/` — Dashboard.tsx, JobCard.tsx, JobDetail.tsx, JobQueue.tsx, Login.tsx
  - `desktop/src/firebase/` — config.ts, jobs.ts
  - `desktop/main.js` — Electron main process
  - `desktop/preload.js` — IPC bridge
  - `desktop/package.json` — build config, version
- `shared/` — types.ts, firebaseConfig.template.ts
- `firebase/` — firestore.rules, storage.rules
- `web/` — static marketing/demo pages

## Key facts
- Mobile: Expo SDK, TypeScript, Firebase Firestore
- Desktop: Electron + React + TypeScript + webpack
- Both apps share Firebase backend
- Build mobile with: `eas build --platform android --profile preview --non-interactive` (in mobile/)
- Build desktop with: `npm run build` (in desktop/)

## When making changes
- Edit files directly — do not reinstall packages unless explicitly needed
- Mobile screens are in `mobile/app/` using Expo Router file-based routing
- Desktop components are in `desktop/src/components/`
