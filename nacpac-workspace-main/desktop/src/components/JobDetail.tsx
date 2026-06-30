import React, { useState } from 'react';
import type { Job, JobStatus } from '@shared/types';
import {
  STATUS_COLORS, STATUS_LABELS, CATEGORY_COLORS,
  STICKER_LABELS, WALLPAPER_LABELS, CUT_LABELS,
  jobTitle,
} from '@shared/types';
import { updateJobStatus, saveOperatorFields } from '../firebase/jobs';

interface Props {
  job:       Job;
  onClose:   () => void;
  onUpdated: () => void;
}

const STATUS_ACTIONS: { status: JobStatus; label: string }[] = [
  { status: 'in_progress', label: '▶  Start Job' },
  { status: 'completed',   label: '✔  Complete'  },
  { status: 'rejected',    label: '✕  Reject'    },
  { status: 'pending',     label: '↺  Reset'      },
];

export default function JobDetail({ job, onClose, onUpdated }: Props) {
  const isCompleted = job.status === 'completed';
  const [materialRollSize, setMaterial] = useState(job.materialRollSize);
  const [inkConsumption, setInk]        = useState(job.inkConsumption);
  const [notes, setNotes]               = useState(job.operatorNotes);
  const [editMode, setEditMode]         = useState(!isCompleted); // completed jobs start read-only
  const [saving, setSaving]             = useState(false);
  const [error, setError]               = useState('');

  const catColor  = CATEGORY_COLORS[job.category];
  const statColor = STATUS_COLORS[job.status];

  async function changeStatus(newStatus: JobStatus) {
    setSaving(true); setError('');
    try {
      await updateJobStatus(job.id, newStatus, materialRollSize, inkConsumption, notes);
      onUpdated();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveFields() {
    setSaving(true); setError('');
    try {
      await saveOperatorFields(job.id, materialRollSize, inkConsumption, notes);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <aside className="detail-panel">

      {/* ── Accent bar ──────────────────────────────────────────── */}
      <div className="detail-accent" style={{ background: `linear-gradient(90deg, ${catColor}, #f5b11b)` }} />

      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="detail-header">
        <div className="detail-header-text">
          <div className="detail-number">{job.jobNumber}</div>
          <div className="detail-title">{jobTitle(job)}</div>
        </div>
        <button className="detail-close" onClick={onClose}>✕</button>
      </div>

      {/* ── Badges ──────────────────────────────────────────────── */}
      <div className="detail-badges">
        <span className="detail-badge" style={{ color: catColor, background: catColor + '22' }}>
          {job.category.toUpperCase()}
        </span>
        <span className="detail-badge" style={{ color: statColor, background: statColor + '22' }}>
          {STATUS_LABELS[job.status]}
        </span>
      </div>

      {/* ── Job Specs ───────────────────────────────────────────── */}
      <div className="detail-section">
        <div className="detail-section-title">Job Specifications</div>
        <div className="detail-specs">
          <SpecRow label="Client"    value={job.clientName} />
          <SpecRow label="Width"     value={`${job.widthInches}"`} />
          <SpecRow label="Height"    value={`${job.heightInches}"`} />
          <SpecRow label="Quantity"  value={`${job.quantity} pcs`} />
          {job.stickerType    && <SpecRow label="Sticker Type"   value={STICKER_LABELS[job.stickerType]} />}
          {job.cuttingProfile && <SpecRow label="Cut Profile"    value={CUT_LABELS[job.cuttingProfile]} />}
          {job.wallpaperType  && <SpecRow label="Wallpaper Type" value={WALLPAPER_LABELS[job.wallpaperType]} />}
          <SpecRow label="Created by" value={job.createdByEmail} />
          <SpecRow label="Created"    value={job.createdAt.toLocaleString()} />
        </div>
      </div>

      {/* ── Files ───────────────────────────────────────────────── */}
      {job.files.length > 0 && (
        <div className="detail-section">
          <div className="detail-section-title">Attachments ({job.files.length})</div>
          {job.files.map((f, i) => (
            <div key={i} className="file-item">
              <span className="file-icon">📄</span>
              <span className="file-name">{f.name}</span>
              <span className="file-size">{(f.size / 1024).toFixed(0)} KB</span>
              <button className="file-download" onClick={() => window.nacpac?.openUrl(f.url)}>
                ↓ Download
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ── Operator Fields ─────────────────────────────────────── */}
      <div className={`detail-section${isCompleted && editMode ? ' op-section-editing' : ''}`}>
        <div className="detail-section-title">
          Operator Fields
          {isCompleted && (
            <button
              className={`op-edit-toggle${editMode ? ' op-edit-toggle-done' : ''}`}
              onClick={() => setEditMode(m => !m)}
            >
              {editMode ? '✓ Done' : '✏ Edit'}
            </button>
          )}
        </div>

        {editMode ? (
          <>
            <label className="op-label">Material Roll Size</label>
            <input
              className="op-input"
              value={materialRollSize}
              onChange={e => setMaterial(e.target.value)}
              placeholder="e.g. 1.07m × 50m glossy vinyl"
            />

            <label className="op-label">Ink Consumption</label>
            <input
              className="op-input"
              value={inkConsumption}
              onChange={e => setInk(e.target.value)}
              placeholder="e.g. 120ml CMYK"
            />

            <label className="op-label">Operator Notes</label>
            <textarea
              className="op-textarea"
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Add production notes or feedback..."
              rows={3}
            />

            <button className="save-fields-btn" onClick={handleSaveFields} disabled={saving}>
              {saving ? 'Saving…' : '💾  Save Fields'}
            </button>
          </>
        ) : (
          <div className="op-readonly">
            <div className="spec-row">
              <span className="spec-label">Material Roll Size</span>
              <span className="spec-value">{materialRollSize || '—'}</span>
            </div>
            <div className="spec-row">
              <span className="spec-label">Ink Consumption</span>
              <span className="spec-value">{inkConsumption || '—'}</span>
            </div>
            <div className="spec-row" style={{ borderBottom: 'none' }}>
              <span className="spec-label">Operator Notes</span>
              <span className="spec-value">{notes || '—'}</span>
            </div>
          </div>
        )}
      </div>

      {/* ── Status Actions ──────────────────────────────────────── */}
      <div className="detail-section">
        <div className="detail-section-title">Update Status</div>
        <div className="status-buttons">
          {STATUS_ACTIONS.filter(s => s.status !== job.status).map(s => (
            <button
              key={s.status}
              className="status-btn"
              style={{ borderColor: STATUS_COLORS[s.status], color: STATUS_COLORS[s.status] }}
              onClick={() => changeStatus(s.status)}
              disabled={saving}
            >
              {s.label}
            </button>
          ))}
        </div>
        {error && <div className="detail-error">{error}</div>}
      </div>


    </aside>
  );
}

function SpecRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="spec-row">
      <span className="spec-label">{label}</span>
      <span className="spec-value">{value}</span>
    </div>
  );
}
