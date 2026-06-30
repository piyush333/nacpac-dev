import React, { useEffect, useState } from 'react';
import '../styles/MachinePanel.css';

interface MachineJob {
  id: string;
  jobNumber: string;
  jobTitle: string;
  status: 'saved' | 'cutting' | 'completed';
  notes: string;
}

interface Props {
  machineType: 'mimaki' | 'ricoh';
  jobs: MachineJob[];
  onDeleteJob?: (jobId: string) => void;
  onStatusChange?: (jobId: string, status: string) => void;
}

export default function MachinePanel({
  machineType,
  jobs,
  onDeleteJob,
  onStatusChange,
}: Props) {
  const machineName = machineType === 'mimaki' ? '🖨️ Mimaki' : '📠 Ricoh';
  const isMimaki = machineType === 'mimaki';

  return (
    <div className="machine-panel">
      <div className="machine-header">
        <h2 className="machine-title">{machineName}</h2>
        <span className="job-count">{jobs.length} job{jobs.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="machine-jobs">
        {jobs.length === 0 ? (
          <div className="machine-empty">
            <div className="empty-icon">
              {isMimaki ? '🖨️' : '📠'}
            </div>
            <p>No jobs</p>
            {isMimaki && <small>Save jobs from the admin app</small>}
          </div>
        ) : (
          jobs.map(job => (
            <div key={job.id} className="machine-job-card">
              <div className="job-header">
                <div className="job-meta">
                  <span className="job-number">{job.jobNumber}</span>
                  <span className={`job-status status-${job.status}`}>
                    {job.status}
                  </span>
                </div>
                {isMimaki && (
                  <button
                    className="delete-btn"
                    onClick={() => onDeleteJob?.(job.id)}
                    title="Remove job"
                  >
                    ✕
                  </button>
                )}
              </div>

              <div className="job-title">{job.jobTitle}</div>

              {job.notes && (
                <div className="job-notes">
                  <strong>Notes:</strong> {job.notes}
                </div>
              )}

              {isMimaki && (
                <div className="job-controls">
                  <select
                    value={job.status}
                    onChange={e => onStatusChange?.(job.id, e.target.value)}
                    className="status-select"
                  >
                    <option value="saved">Saved</option>
                    <option value="cutting">Cutting</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
