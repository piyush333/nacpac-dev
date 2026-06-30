// ─────────────────────────────────────────────────────────────────
//  NACPAC Production System — Shared Types
//  Source of truth for mobile + desktop apps
// ─────────────────────────────────────────────────────────────────

// ── Job categories ────────────────────────────────────────────────
export type JobCategory = 'stickers' | 'wallpapers' | 'ntr';

// ── Sticker sub-types ─────────────────────────────────────────────
export type StickerType =
  | 'vinyl'
  | 'transparent'
  | 'holographic'
  | 'glitter'
  | 'gold_chrome'
  | 'chrome'
  | 'optical';

// ── Cutting profiles (stickers only) ─────────────────────────────
export type CuttingProfile = 'custom_cut' | 'square' | 'round' | 'rectangle';

// ── Wallpaper sub-types ───────────────────────────────────────────
export type WallpaperType = 'canvas' | 'pvc' | 'non_woven' | 'grained' | 'stroke' | 'leatherette';

// ── Job status ────────────────────────────────────────────────────
export type JobStatus = 'pending' | 'in_progress' | 'completed' | 'rejected';

// ── Machine type ──────────────────────────────────────────────────
export type MachineName = 'mimaki' | 'ricoh';

// ── Attached file ─────────────────────────────────────────────────
export interface JobFile {
  name: string;
  url:  string;    // Firebase Storage download URL
  size: number;    // bytes
  type: string;    // MIME type  e.g. application/pdf
  path: string;    // Storage path (for deletion)
}

// ── Core job document ─────────────────────────────────────────────
export interface Job {
  id:         string;
  jobNumber:  string;           // "JOB-0042"

  // Category & sub-type
  category:       JobCategory;
  stickerType?:   StickerType;       // stickers only
  cuttingProfile?: CuttingProfile;   // stickers only
  wallpaperType?: WallpaperType;     // wallpapers only

  // Dimensions & quantity
  widthInches:  number;
  heightInches: number;
  quantity:     number;

  // Client & files
  clientName: string;
  files:      JobFile[];

  // Status & timestamps
  status:    JobStatus;
  createdAt: Date;
  updatedAt: Date;

  // Machine
  machine?:  MachineName;

  // Who created it
  createdBy:      string;   // Firebase Auth UID
  createdByEmail: string;

  // Operator fields (filled on Windows dashboard)
  materialRollSize: string;
  inkConsumption:   string;
  operatorNotes:    string;
}

// ── Notification document ─────────────────────────────────────────
export interface Notification {
  id:        string;
  jobId:     string;
  jobNumber: string;
  jobTitle:  string;          // e.g. "Vinyl Stickers — Jain Traders"
  type:      'new_job' | 'status_changed';
  message:   string;
  read:      boolean;
  createdAt: Date;
}

// ── Display helpers ───────────────────────────────────────────────
export const CATEGORY_LABELS: Record<JobCategory, string> = {
  stickers:   '🏷️  Stickers',
  wallpapers: '🖼️  Wallpapers',
  ntr:        '📦  NTR',
};

export const CATEGORY_COLORS: Record<JobCategory, string> = {
  stickers:   '#6366f1',
  wallpapers: '#06b6d4',
  ntr:        '#f59e0b',
};

export const STICKER_LABELS: Record<StickerType, string> = {
  vinyl:        'Vinyl',
  transparent:  'Transparent',
  holographic:  'Holographic',
  glitter:      'Glitter',
  gold_chrome:  'Gold Chrome',
  chrome:       'Chrome',
  optical:      'Optical',
};

export const CUT_LABELS: Record<CuttingProfile, string> = {
  custom_cut: 'Custom Cut',
  square:     'Square',
  round:      'Round',
  rectangle:  'Rectangle',
};

export const WALLPAPER_LABELS: Record<WallpaperType, string> = {
  canvas:     'Canvas',
  pvc:        'PVC',
  non_woven:  'Non-woven',
  grained:    'Grained',
  stroke:     'Stroke',
  leatherette: 'Leatherette',
};

export const STATUS_COLORS: Record<JobStatus, string> = {
  pending:     '#f59e0b',
  in_progress: '#3b82f6',
  completed:   '#22c55e',
  rejected:    '#ef4444',
};

export const STATUS_LABELS: Record<JobStatus, string> = {
  pending:     'Pending',
  in_progress: 'In Progress',
  completed:   'Completed',
  rejected:    'Rejected',
};

// ── Derive a short human-readable job title ───────────────────────
export function jobTitle(job: Pick<Job,
  'category' | 'stickerType' | 'wallpaperType' | 'clientName'
>): string {
  let sub = '';
  if (job.category === 'stickers' && job.stickerType)
    sub = STICKER_LABELS[job.stickerType] + ' Stickers';
  else if (job.category === 'wallpapers' && job.wallpaperType)
    sub = WALLPAPER_LABELS[job.wallpaperType] + ' Wallpaper';
  else
    sub = 'NTR';
  return `${sub} — ${job.clientName}`;
}
