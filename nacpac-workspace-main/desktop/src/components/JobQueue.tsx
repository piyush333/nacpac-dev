import React from 'react';
import type { Job } from '@shared/types';
import JobCard from './JobCard';

interface Props {
  jobs: Job[];
  onSelect: (job: Job) => void;
  selectedId?: string;
}

export default function JobQueue({ jobs, onSelect, selectedId }: Props) {
  if (jobs.length === 0) {
    return (
      <div className="queue-empty">
        <div className="queue-empty-icon">📋</div>
        <div className="queue-empty-text">No jobs in queue</div>
        <div className="queue-empty-sub">New jobs from the admin app will appear here in real-time.</div>
      </div>
    );
  }

  return (
    <div className="job-queue">
      <div className="queue-header">
        <span>{jobs.length} job{jobs.length !== 1 ? 's' : ''}</span>
      </div>
      <div className="queue-list">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            selected={job.id === selectedId}
            onClick={() => onSelect(job)}
          />
        ))}
      </div>
    </div>
  );
}
