# NACPAC Production System — Complete Codebase

## Project Structure
```
nacpac/
├── shared/
│   └── types.ts              (Job types, status enums, labels)
├── mobile/                   (Expo/React Native - Admin App)
│   ├── firebase/
│   │   ├── config.ts         (Firebase init)
│   │   ├── clients.ts        (Client CRUD)
│   │   └── jobs.ts           (Job CRUD + stats)
│   ├── app/
│   │   ├── (tabs)/
│   │   │   ├── index.tsx     (Home dashboard)
│   │   │   ├── new-job.tsx   (3-step job form)
│   │   │   ├── clients.tsx   (Client list)
│   │   │   └── jobs.tsx      (Job list)
│   │   ├── login.tsx         (Auth screen)
│   │   └── _layout.tsx       (Navigation)
│   └── components/
│       └── JobCard.tsx       (Job display)
│
├── desktop/                  (Electron - Operator Dashboard)
│   ├── src/
│   │   ├── firebase/         (Job + notification queries)
│   │   ├── components/
│   │   │   ├── Dashboard.tsx (Main layout + sidebar)
│   │   │   ├── JobQueue.tsx  (Live job list)
│   │   │   ├── JobDetail.tsx (Job details + controls)
│   │   │   └── Login.tsx     (Auth)
│   │   ├── App.tsx           (Auth router)
│   │   └── styles/           (CSS)
│   └── package.json
│
├── firebase/                 (Firestore + Storage rules)
│   ├── firestore.rules
│   └── storage.rules
│
└── demo.html                 (Interactive UI preview)
```

---

## Core Types (`shared/types.ts`)

```typescript
// Job categories
export type JobCategory = 'stickers' | 'wallpapers' | 'ntr';

// Sticker sub-types
export type StickerType = 'vinyl' | 'transparent' | 'holographic' | 'glitter' | 'gold_chrome';

// Cutting profiles (stickers only)
export type CuttingProfile = 'custom_cut' | 'square' | 'round' | 'rectangle';

// Wallpaper sub-types
export type WallpaperType = 'canvas' | 'pvc' | 'non_woven';

// Job status
export type JobStatus = 'pending' | 'in_progress' | 'completed' | 'rejected';

// File attachment
export interface JobFile {
  name: string;
  url: string;           // Firebase Storage download URL
  size: number;          // bytes
  type: string;          // MIME type
  path: string;          // Storage path
}

// Core job document
export interface Job {
  id: string;
  jobNumber: string;                    // "JOB-0042"
  category: JobCategory;
  stickerType?: StickerType;
  cuttingProfile?: CuttingProfile;
  wallpaperType?: WallpaperType;
  widthInches: number;
  heightInches: number;
  quantity: number;
  clientName: string;
  files: JobFile[];
  status: JobStatus;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;                    // Firebase Auth UID
  createdByEmail: string;
  materialRollSize: string;             // Operator fills this
  inkConsumption: string;               // Operator fills this
  operatorNotes: string;                // Operator fills this
}

// Display helpers
export const CATEGORY_LABELS: Record<JobCategory, string> = {
  stickers: '🏷️ Stickers',
  wallpapers: '🖼️ Wallpapers',
  ntr: '📦 NTR',
};

export const STATUS_COLORS: Record<JobStatus, string> = {
  pending: '#f59e0b',
  in_progress: '#3b82f6',
  completed: '#22c55e',
  rejected: '#ef4444',
};
```

---

## Mobile App

### Firebase Config (`mobile/firebase/config.ts`)
```typescript
import { initializeApp, getApps } from 'firebase/app';
import { getAuth, initializeAuth, getReactNativePersistence } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import AsyncStorage from '@react-native-async-storage/async-storage';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "nacpac-production-4134a.firebaseapp.com",
  projectId: "nacpac-production-4134a",
  storageBucket: "nacpac-production-4134a.firebasestorage.app",
  messagingSenderId: "371880247454",
  appId: "1:371880247454:web:b9ae971b4aa16bea673b8f"
};

const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const auth = getApps().length === 1
  ? initializeAuth(app, {
      persistence: getReactNativePersistence(AsyncStorage),
    })
  : getAuth(app);

export const db = getFirestore(app);
export const storage = getStorage(app);
```

### Client Management (`mobile/firebase/clients.ts`)
```typescript
import { collection, addDoc, query, orderBy, onSnapshot, where, getDocs, Timestamp } from 'firebase/firestore';
import { db } from './config';

export interface Client {
  id: string;
  name: string;
  createdAt: Date;
}

export async function addClient(name: string): Promise<void> {
  const trimmed = name.trim();
  if (!trimmed) throw new Error('Client name cannot be empty');

  // Check for duplicate
  const existing = await getDocs(
    query(collection(db, 'clients'), where('name', '==', trimmed))
  );
  if (!existing.empty) throw new Error(`Client "${trimmed}" already exists`);

  await addDoc(collection(db, 'clients'), {
    name: trimmed,
    createdAt: Timestamp.now(),
  });
}

export function subscribeToClients(
  callback: (clients: Client[]) => void,
): () => void {
  const q = query(collection(db, 'clients'), orderBy('name', 'asc'));
  return onSnapshot(q, snap => {
    callback(snap.docs.map(d => ({
      id: d.id,
      name: d.data().name as string,
      createdAt: d.data().createdAt?.toDate() ?? new Date(),
    })));
  });
}
```

### Job Operations (`mobile/firebase/jobs.ts`) - Key Functions
```typescript
// Create new job
export async function createJob(data: CreateJobInput): Promise<string> {
  const user = auth.currentUser;
  if (!user) throw new Error('Not authenticated');

  const jobNumber = await getNextJobNumber();
  const now = Timestamp.now();

  const docRef = await addDoc(collection(db, 'jobs'), {
    jobNumber,
    category: data.category,
    stickerType: data.stickerType ?? null,
    cuttingProfile: data.cuttingProfile ?? null,
    wallpaperType: data.wallpaperType ?? null,
    widthInches: data.widthInches,
    heightInches: data.heightInches,
    quantity: data.quantity,
    clientName: data.clientName,
    files: data.files,
    status: 'pending',
    createdAt: now,
    updatedAt: now,
    createdBy: user.uid,
    createdByEmail: user.email ?? '',
    materialRollSize: '',
    inkConsumption: '',
    operatorNotes: '',
  });

  // Notify operator
  await addDoc(collection(db, 'notifications'), {
    jobId: docRef.id,
    jobNumber,
    jobTitle: jobTitle(data),
    type: 'new_job',
    message: `New job: ${jobTitle(data)}`,
    read: false,
    createdAt: now,
  });

  return docRef.id;
}

// File upload
export async function uploadFile(
  localUri: string,
  fileName: string,
  mimeType: string,
  jobId: string,
  onProgress?: (pct: number) => void,
): Promise<JobFile> {
  const resp = await fetch(localUri);
  const blob = await resp.blob();
  const path = `jobs/${jobId}/${Date.now()}_${fileName}`;
  const task = uploadBytesResumable(ref(storage, path), blob, { contentType: mimeType });

  return new Promise((resolve, reject) => {
    task.on(
      'state_changed',
      s => onProgress?.(Math.round((s.bytesTransferred / s.totalBytes) * 100)),
      reject,
      async () => {
        const url = await getDownloadURL(task.snapshot.ref);
        resolve({ name: fileName, url, size: blob.size, type: mimeType, path });
      },
    );
  });
}

// Dashboard stats
export async function getDashboardStats(): Promise<DashboardStats> {
  const [pend, prog, comp, rej, stick, wall, ntr] = await Promise.all([
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'pending'))),
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'in_progress'))),
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'completed'))),
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'rejected'))),
    getCountFromServer(query(collection(db, 'jobs'), where('category', '==', 'stickers'))),
    getCountFromServer(query(collection(db, 'jobs'), where('category', '==', 'wallpapers'))),
    getCountFromServer(query(collection(db, 'jobs'), where('category', '==', 'ntr'))),
  ]);
  return {
    pending: pend.data().count,
    in_progress: prog.data().count,
    completed: comp.data().count,
    rejected: rej.data().count,
    stickers: stick.data().count,
    wallpapers: wall.data().count,
    ntr: ntr.data().count,
  };
}
```

---

## Desktop App (Windows Operator Dashboard)

### Main App (`desktop/src/App.tsx`)
```typescript
import React, { useEffect, useState } from 'react';
import { onAuthStateChanged, User } from 'firebase/auth';
import { auth } from './firebase/config';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    return onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner" />
        <p>Connecting to NACPAC...</p>
      </div>
    );
  }

  return user ? <Dashboard user={user} /> : <Login />;
}
```

### Dashboard Component (`desktop/src/components/Dashboard.tsx`)
**Features:**
- Real-time job queue with live updates from Firestore
- Sidebar with status & category filters
- Job detail panel on the right
- Notification center (🔔 badge)
- Live status counts

**Key Functions:**
```typescript
export default function Dashboard({ user }: Props) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selected, setSelected] = useState<Job | null>(null);
  const [stats, setStats] = useState<Stats>({
    pending: 0, in_progress: 0, completed: 0, rejected: 0
  });
  const [filter, setFilter] = useState<FilterValue>('all');

  useEffect(() => {
    const unsub = subscribeToJobs(newJobs => {
      setJobs(newJobs);
      window.nacpac?.setBadge(newJobs.filter(j => j.status === 'pending').length);
    });
    loadStats();
    return unsub;
  }, []);

  // Filter jobs by status or category
  const filteredJobs = (() => {
    if (filter === 'all') return jobs;
    if (filter === 'stickers') return jobs.filter(j => j.category === 'stickers');
    if (filter === 'wallpapers') return jobs.filter(j => j.category === 'wallpapers');
    if (filter === 'ntr') return jobs.filter(j => j.category === 'ntr');
    return jobs.filter(j => j.status === filter as JobStatus);
  })();

  return (
    <div className="dashboard">
      <aside className="sidebar">
        {/* Status filters + category filters */}
      </aside>
      <main className="main-content">
        {/* Topbar + notifications dropdown */}
        <JobQueue jobs={filteredJobs} onSelect={setSelected} />
      </main>
      {selected && (
        <JobDetail job={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}
```

### Job Detail Panel (`desktop/src/components/JobDetail.tsx`)
**Features:**
- View all job specifications
- Download attached files
- Edit operator fields (material roll size, ink consumption, notes)
- Change job status (Start → In Progress, Complete, or Reject)
- Color-coded badges for category & status

**Key Functions:**
```typescript
export default function JobDetail({ job, onClose, onUpdated }: Props) {
  const [materialRollSize, setMaterial] = useState(job.materialRollSize);
  const [inkConsumption, setInk] = useState(job.inkConsumption);
  const [notes, setNotes] = useState(job.operatorNotes);
  const [saving, setSaving] = useState(false);

  async function changeStatus(newStatus: JobStatus) {
    setSaving(true);
    try {
      await updateJobStatus(job.id, newStatus, materialRollSize, inkConsumption, notes);
      onUpdated();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <aside className="detail-panel">
      {/* Job specs table */}
      <div className="detail-specs">
        <SpecRow label="Client" value={job.clientName} />
        <SpecRow label="Width" value={`${job.widthInches}"`} />
        <SpecRow label="Height" value={`${job.heightInches}"`} />
        <SpecRow label="Quantity" value={`${job.quantity} pcs`} />
      </div>

      {/* Attachments */}
      {job.files.map(f => (
        <div key={f.name} className="file-item">
          <button onClick={() => window.nacpac?.openUrl(f.url)}>
            ↓ Download {f.name}
          </button>
        </div>
      ))}

      {/* Operator fields */}
      <input value={materialRollSize} onChange={e => setMaterial(e.target.value)} placeholder="Material..." />
      <input value={inkConsumption} onChange={e => setInk(e.target.value)} placeholder="Ink..." />
      <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Notes..." />

      {/* Status buttons */}
      <div className="status-buttons">
        <button onClick={() => changeStatus('in_progress')}>▶ Start Job</button>
        <button onClick={() => changeStatus('completed')}>✔ Complete</button>
        <button onClick={() => changeStatus('rejected')}>✕ Reject</button>
      </div>
    </aside>
  );
}
```

---

## Firebase Operations (`desktop/src/firebase/jobs.ts`)

```typescript
// Real-time job subscription
export function subscribeToJobs(callback: (jobs: Job[]) => void): () => void {
  const q = query(collection(db, 'jobs'), orderBy('createdAt', 'desc'));
  return onSnapshot(q, snap => {
    callback(snap.docs.map(docToJob));
  });
}

// Update job status + operator fields
export async function updateJobStatus(
  jobId: string,
  status: JobStatus,
  materialRollSize: string,
  inkConsumption: string,
  operatorNotes: string,
): Promise<void> {
  await updateDoc(doc(db, 'jobs', jobId), {
    status,
    materialRollSize,
    inkConsumption,
    operatorNotes,
    updatedAt: Timestamp.now(),
  });

  // Notify admin
  const job = await getDoc(doc(db, 'jobs', jobId));
  const data = job.data();
  await addDoc(collection(db, 'notifications'), {
    jobId,
    jobNumber: data.jobNumber,
    jobTitle: `${data.jobNumber} — ${data.clientName}`,
    type: 'status_changed',
    message: `Status changed to: ${status}`,
    read: false,
    createdAt: Timestamp.now(),
  });
}

// Get job statistics
export async function getJobStats(): Promise<{ pending: number; in_progress: number; completed: number; rejected: number }> {
  const [pend, prog, comp, rej] = await Promise.all([
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'pending'))),
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'in_progress'))),
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'completed'))),
    getCountFromServer(query(collection(db, 'jobs'), where('status', '==', 'rejected'))),
  ]);
  return {
    pending: pend.data().count,
    in_progress: prog.data().count,
    completed: comp.data().count,
    rejected: rej.data().count,
  };
}
```

---

## Data Flow

### Admin Creates Job (Mobile)
1. Admin fills 3-step form (category → specs → details)
2. Uploads files (auto-uploaded to Firebase Storage)
3. Clicks "Send to Production"
4. **Firestore:** `jobs/{jobId}` created with `status: pending`
5. **Firestore:** `notifications/{notifId}` created for operator

### Operator Updates Status (Windows)
1. Operator sees job appear in real-time queue
2. Clicks job → detail panel opens
3. Adds production notes, material info, ink consumption
4. Clicks "▶ Start Job", "✔ Complete", or "✕ Reject"
5. **Firestore:** Job document updated with new status
6. **Firestore:** Notification created for admin
7. **Mobile:** Admin sees real-time status update via `subscribeToJobs()`

---

## Setup Checklist

- [ ] Firebase project created (firebaseapp.com)
- [ ] Firestore enabled (Production mode, asia-south1 region)
- [ ] Storage enabled
- [ ] Authentication: Email/Password enabled
- [ ] Config added to `mobile/firebase/config.ts`
- [ ] Config added to `desktop/src/firebase/config.ts`
- [ ] Security rules deployed: `firebase deploy --only firestore:rules,storage`
- [ ] Test users created: admin@nacpac.com, operator@nacpac.com
- [ ] Mobile: `npm install && npx expo start`
- [ ] Desktop: `npm install && npm run dev`
