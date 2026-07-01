import { db } from './config';
import { collection, query, where, onSnapshot, getDocs } from 'firebase/firestore';

export function subscribeToJobs(callback: (jobs: any[]) => void) {
  const q = query(collection(db, 'jobs'));
  return onSnapshot(q, (snapshot) => {
    const jobs = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    callback(jobs);
  });
}

export async function getJobStats() {
  const snapshot = await getDocs(collection(db, 'jobs'));
  const stats = {
    pending: 0,
    in_progress: 0,
    completed: 0,
    rejected: 0,
  };

  snapshot.docs.forEach(doc => {
    const status = doc.data().status;
    if (status in stats) {
      stats[status as keyof typeof stats]++;
    }
  });

  return stats;
}
