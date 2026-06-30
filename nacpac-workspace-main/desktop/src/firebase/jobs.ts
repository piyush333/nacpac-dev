// ─────────────────────────────────────────────────────────────────
//  NACPAC Desktop — Firestore Operations
// ─────────────────────────────────────────────────────────────────
import {
  collection, query, orderBy, onSnapshot,
  doc, updateDoc, deleteDoc, Timestamp, limit, where,
  getCountFromServer,
} from 'firebase/firestore';
import { db } from './config';
import type { Job, JobStatus, Notification } from '@shared/types';

// ── Map Firestore doc → Job ───────────────────────────────────────
function docToJob(d: any): Job {
  const data = d.data();
  return {
    id:               d.id,
    jobNumber:        data.jobNumber,
    category:         data.category,
    stickerType:      data.stickerType      ?? undefined,
    cuttingProfile:   data.cuttingProfile   ?? undefined,
    wallpaperType:    data.wallpaperType    ?? undefined,
    widthInches:      data.widthInches,
    heightInches:     data.heightInches,
    quantity:         data.quantity,
    clientName:       data.clientName,
    files:            data.files            ?? [],
    status:           data.status,
    machine:          data.machine          ?? undefined,
    createdAt:        data.createdAt?.toDate()  ?? new Date(),
    updatedAt:        data.updatedAt?.toDate()  ?? new Date(),
    createdBy:        data.createdBy,
    createdByEmail:   data.createdByEmail   ?? '',
    materialRollSize: data.materialRollSize ?? '',
    inkConsumption:   data.inkConsumption   ?? '',
    operatorNotes:    data.operatorNotes    ?? '',
  };
}

// ── Real-time job queue listener ──────────────────────────────────
export function subscribeToJobs(
  callback: (jobs: Job[]) => void,
): () => void {
  const q = query(
    collection(db, 'jobs'),
    orderBy('createdAt', 'desc'),
    limit(200),
  );

  let retryTimeout: ReturnType<typeof setTimeout> | null = null;
  let unsub: (() => void) | null = null;
  let active = true;

  function attach() {
    unsub = onSnapshot(
      q,
      snap => callback(snap.docs.map(docToJob)),
      _err => {
        if (!active) return;
        if (unsub) { unsub(); unsub = null; }
        retryTimeout = setTimeout(() => { if (active) attach(); }, 3000);
      },
    );
  }

  attach();

  return () => {
    active = false;
    if (retryTimeout) clearTimeout(retryTimeout);
    if (unsub) unsub();
  };
}

// ── Update job status + operator fields ──────────────────────────
export async function updateJobStatus(
  jobId:            string,
  status:           JobStatus,
  materialRollSize: string,
  inkConsumption:   string,
  operatorNotes:    string,
): Promise<void> {
  await updateDoc(doc(db, 'jobs', jobId), {
    status,
    materialRollSize,
    inkConsumption,
    operatorNotes,
    updatedAt: Timestamp.now(),
  });
}

// ── Save operator fields without changing status ──────────────────
export async function saveOperatorFields(
  jobId:            string,
  materialRollSize: string,
  inkConsumption:   string,
  operatorNotes:    string,
): Promise<void> {
  await updateDoc(doc(db, 'jobs', jobId), {
    materialRollSize,
    inkConsumption,
    operatorNotes,
    updatedAt: Timestamp.now(),
  });
}

// ── Delete a job ─────────────────────────────────────────────────
export async function deleteJob(jobId: string): Promise<void> {
  await deleteDoc(doc(db, 'jobs', jobId));
}

// ── Dashboard stats by status ─────────────────────────────────────
export async function getJobStats(): Promise<{
  pending: number; in_progress: number; completed: number; rejected: number;
}> {
  const statuses: JobStatus[] = ['pending', 'in_progress', 'completed', 'rejected'];
  const counts = await Promise.all(
    statuses.map(s => getCountFromServer(query(collection(db, 'jobs'), where('status', '==', s)))),
  );
  return {
    pending:     counts[0].data().count,
    in_progress: counts[1].data().count,
    completed:   counts[2].data().count,
    rejected:    counts[3].data().count,
  };
}

// ── Subscribe to unread notifications ────────────────────────────
export function subscribeToNotifications(
  callback: (notifs: Notification[]) => void,
): () => void {
  const q = query(
    collection(db, 'notifications'),
    where('read', '==', false),
    orderBy('createdAt', 'desc'),
    limit(50),
  );
  return onSnapshot(q, snap => {
    const notifs: Notification[] = snap.docs.map(d => {
      const data = d.data();
      return {
        id:        d.id,
        jobId:     data.jobId,
        jobNumber: data.jobNumber,
        jobTitle:  data.jobTitle,
        type:      data.type,
        message:   data.message,
        read:      data.read,
        createdAt: data.createdAt?.toDate() ?? new Date(),
      };
    });
    callback(notifs);
  });
}
