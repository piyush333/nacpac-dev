import React, { useEffect, useRef, useState } from 'react';
import { User, signOut } from 'firebase/auth';
import { auth } from '../firebase/config';
import { subscribeToJobs, subscribeToNotifications, getJobStats } from '../firebase/jobs';
import JobQueue from './JobQueue';
import JobDetail from './JobDetail';
import type { Job, JobStatus, Notification } from '@shared/types';
import { STATUS_COLORS, CATEGORY_COLORS, jobTitle } from '@shared/types';

interface Props { user: User }

interface Stats {
  pending: number; in_progress: number; completed: number; rejected: number;
}

declare global {
  interface Window {
    nacpac: {
      openUrl:  (url: string) => void;
      notify:   (title: string, body: string) => void;
      setBadge: (count: number) => void;
    };
  }
}

type FilterValue = JobStatus | 'all' | 'stickers' | 'wallpapers' | 'ntr';

export default function Dashboard({ user }: Props) {
  const [jobs, setJobs]             = useState<Job[]>([]);
  const [selected, setSelected]     = useState<Job | null>(null);
  const [stats, setStats]           = useState<Stats>({ pending: 0, in_progress: 0, completed: 0, rejected: 0 });
  const [filter, setFilter]         = useState<FilterValue>('all');
  const [notifs, setNotifs]         = useState<Notification[]>([]);
  const [showNotifs, setShowNotifs] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const prevJobIds    = useRef<Set<string>>(new Set());
  const shownNotifIds = useRef<Set<string>>(new Set());
  const searchRef     = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const unsub = subscribeToJobs(newJobs => {
      newJobs.forEach(j => {
        if (!prevJobIds.current.has(j.id) && prevJobIds.current.size > 0) {
          window.nacpac?.notify(
            `New Job: ${j.jobNumber}`,
            jobTitle(j),
          );
        }
        prevJobIds.current.add(j.id);
      });
      setJobs(newJobs);
      window.nacpac?.setBadge(newJobs.filter(j => j.status === 'pending').length);
    });

    const unsubN = subscribeToNotifications(allNotifs => {
      // Only show notifications that haven't been shown before
      const newNotifs = allNotifs.filter(n => !shownNotifIds.current.has(n.id));
      newNotifs.forEach(n => {
        shownNotifIds.current.add(n.id);
        window.nacpac?.notify(n.jobNumber, n.message);
      });
      setNotifs(allNotifs);
    });

    loadStats();

    // Ctrl+F → focus search
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => { unsub(); unsubN(); window.removeEventListener('keydown', onKey); };
  }, []);

  useEffect(() => { loadStats(); }, [jobs]);

  async function loadStats() {
    try {
      const s = await getJobStats();
      setStats(s);
    } catch (_) { /* ignore */ }
  }

  // Apply filter + text search
  const filteredJobs = (() => {
    let result: Job[];
    if (filter === 'all')        result = jobs;
    else if (filter === 'stickers')   result = jobs.filter(j => j.category === 'stickers');
    else if (filter === 'wallpapers') result = jobs.filter(j => j.category === 'wallpapers');
    else if (filter === 'ntr')        result = jobs.filter(j => j.category === 'ntr');
    else result = jobs.filter(j => j.status === filter as JobStatus);

    const q = searchQuery.trim().toLowerCase();
    if (q) {
      result = result.filter(j =>
        j.jobNumber.toLowerCase().includes(q) ||
        j.clientName.toLowerCase().includes(q) ||
        jobTitle(j).toLowerCase().includes(q)
      );
    }
    return result;
  })();

  // Category counts from current jobs
  const catCounts = {
    stickers:   jobs.filter(j => j.category === 'stickers').length,
    wallpapers: jobs.filter(j => j.category === 'wallpapers').length,
    ntr:        jobs.filter(j => j.category === 'ntr').length,
  };

  function filterLabel(f: FilterValue): string {
    if (f === 'all')       return 'All Jobs';
    if (f === 'stickers')  return 'Stickers';
    if (f === 'wallpapers')return 'Wallpapers';
    if (f === 'ntr')       return 'NTR';
    return f.replace('_', ' ');
  }

  return (
    <div className="dashboard">

      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="sidebar-logo-container">
            <img src="assets/icon.png" alt="NACPAC" className="sidebar-mascot" />
            <div>
              <div className="sidebar-logo">
                <span className="logo-nac">nac</span><span className="logo-pac">pac</span>
              </div>
              <div className="sidebar-subtitle">Production Dashboard</div>
            </div>
          </div>
          <div className="sidebar-header">
            <div className="user-email">{user.email}</div>
            <button className="signout-btn" onClick={() => signOut(auth)}>Sign Out</button>
          </div>
        </div>

        {/* Status filters */}
        <div className="sidebar-group-label">Status</div>
        {(['pending','in_progress','completed','rejected'] as JobStatus[]).map(s => (
          <button
            key={s}
            className={`sidebar-item ${filter === s ? 'sidebar-item-active' : ''}`}
            onClick={() => setFilter(s)}
            style={filter === s ? { borderLeftColor: STATUS_COLORS[s] } : {}}
          >
            <span className="si-dot" style={{ background: STATUS_COLORS[s] }} />
            <span className="si-label">{s.replace('_', ' ')}</span>
            <span className="si-count" style={filter === s ? { color: STATUS_COLORS[s] } : {}}>
              {stats[s]}
            </span>
          </button>
        ))}
        <button
          className={`sidebar-item ${filter === 'all' ? 'sidebar-item-active' : ''}`}
          onClick={() => setFilter('all')}
        >
          <span className="si-dot" style={{ background: '#9b7bde' }} />
          <span className="si-label">All Jobs</span>
          <span className="si-count" style={filter === 'all' ? { color: '#9b7bde' } : {}}>{jobs.length}</span>
        </button>

        {/* Category filters */}
        <div className="sidebar-group-label" style={{ marginTop: 20 }}>Category</div>
        {([
          ['stickers',   '🏷️', CATEGORY_COLORS.stickers,   catCounts.stickers],
          ['wallpapers', '🖼️', CATEGORY_COLORS.wallpapers,  catCounts.wallpapers],
          ['ntr',        '📦', CATEGORY_COLORS.ntr,         catCounts.ntr],
        ] as [FilterValue, string, string, number][]).map(([cat, icon, color, count]) => (
          <button
            key={cat}
            className={`sidebar-item ${filter === cat ? 'sidebar-item-active' : ''}`}
            onClick={() => setFilter(cat)}
            style={filter === cat ? { borderLeftColor: color } : {}}
          >
            <span className="si-icon">{icon}</span>
            <span className="si-label">{cat}</span>
            <span className="si-count" style={filter === cat ? { color } : {}}>{count}</span>
          </button>
        ))}
      </aside>

      {/* ── Main ────────────────────────────────────────────────── */}
      <main className="main-content">

        {/* Topbar */}
        <div className="topbar">
          <div className="topbar-title">
            Job Queue
            {filter !== 'all' && (
              <span className="topbar-filter"> — {filterLabel(filter)}</span>
            )}
          </div>
          <div className="topbar-right">
            {/* Quick-search completed jobs */}
            <button
              className={`completed-search-btn${filter === 'completed' ? ' completed-search-btn-active' : ''}`}
              title="Filter & search completed jobs"
              onClick={() => {
                setFilter('completed');
                setTimeout(() => searchRef.current?.focus(), 50);
              }}
            >
              ✔ Completed
            </button>

          <div className={`search-wrap${filter === 'completed' ? ' search-wrap-completed' : ''}`}>
              <span className="search-icon">&#128269;</span>
              <input
                ref={searchRef}
                className="search-input"
                type="text"
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder={filter === 'completed' ? 'Search completed jobs…' : 'Search jobs… (Ctrl+F)'}
              />
              {searchQuery && (
                <button className="search-clear" title="Clear search" onClick={() => setSearchQuery('')}>✕</button>
              )}
            </div>
            <button className="notif-btn" onClick={() => setShowNotifs(!showNotifs)}>
              🔔
              {notifs.length > 0 && (
                <span className="notif-badge">{notifs.length}</span>
              )}
            </button>
          </div>
        </div>

        {/* Notifications dropdown */}
        {showNotifs && (
          <div className="notif-panel">
            <div className="notif-header">Notifications</div>
            {notifs.length === 0
              ? <div className="notif-empty">No new notifications</div>
              : notifs.map(n => (
                <div key={n.id} className="notif-item" onClick={() => {
                  const j = jobs.find(x => x.id === n.jobId);
                  if (j) { setSelected(j); setShowNotifs(false); }
                }}>
                  <div className="notif-title">{n.jobNumber} — {n.jobTitle}</div>
                  <div className="notif-msg">{n.message}</div>
                </div>
              ))
            }
          </div>
        )}

        <JobQueue
          jobs={filteredJobs}
          onSelect={setSelected}
          selectedId={selected?.id}
        />
      </main>

      {/* ── Detail panel ────────────────────────────────────────── */}
      {selected && (
        <JobDetail
          key={selected.id}
          job={selected}
          onClose={() => setSelected(null)}
          onUpdated={() => { setSelected(null); loadStats(); }}
        />
      )}
    </div>
  );
}
