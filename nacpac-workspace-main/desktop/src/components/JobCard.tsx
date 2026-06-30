import React from 'react';
import type { Job } from '@shared/types';
import {
  STATUS_COLORS, STATUS_LABELS,
  CATEGORY_COLORS,
  jobTitle,
  STICKER_LABELS, WALLPAPER_LABELS, CUT_LABELS,
} from '@shared/types';

interface Props {
  job:      Job;
  selected: boolean;
  onClick:  () => void;
}

function timeAgo(date: Date): string {
  const diff = Date.now() - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1)   return 'just now';
  if (mins < 60)  return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)   return `${hrs}h ago`;
  return date.toLocaleDateString('en-IN', { day: '2-digit', month: 'short' });
}

function subLabel(job: Job): string {
  if (job.category === 'stickers') {
    const s = job.stickerType   ? STICKER_LABELS[job.stickerType]   : '';
    const c = job.cuttingProfile ? ` · ${CUT_LABELS[job.cuttingProfile]}` : '';
    return s + c;
  }
  if (job.category === 'wallpapers') {
    return job.wallpaperType ? WALLPAPER_LABELS[job.wallpaperType] : 'Wallpaper';
  }
  return 'NTR';
}

export default function JobCard({ job, selected, onClick }: Props) {
  const catColor  = CATEGORY_COLORS[job.category];
  const statColor = STATUS_COLORS[job.status];

  return (
    <div
      className={`job-card ${selected ? 'job-card-selected' : ''}`}
      onClick={onClick}
      style={{ borderLeftColor: catColor }}
    >
      <div className="jc-top">
        <span className="jc-number">{job.jobNumber}</span>
        <span className="jc-time">{timeAgo(job.createdAt)}</span>
      </div>

      <div className="jc-title">{jobTitle(job)}</div>
      <div className="jc-sub">
        {subLabel(job)}
        {job.machine && (
          <>
            <br />
            <span className="jc-producer">Produced by {job.machine.charAt(0).toUpperCase() + job.machine.slice(1)}</span>
          </>
        )}
      </div>

      <div className="jc-bottom">
        <span className="jc-status" style={{ color: statColor, background: statColor + '22' }}>
          <span className="jc-dot" style={{ background: statColor }} />
          {STATUS_LABELS[job.status]}
        </span>
        <span className="jc-dims">
          {job.widthInches}″ × {job.heightInches}″  ·  {job.quantity} pcs
        </span>
        {job.files.length > 0 && (
          <span className="jc-files">📎 {job.files.length}</span>
        )}
      </div>
    </div>
  );
}
