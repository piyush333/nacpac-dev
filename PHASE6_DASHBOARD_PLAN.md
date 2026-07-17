# Phase 6: Dashboard UI Implementation Plan

**Status**: Planning  
**Objective**: Build real-time agent status dashboard with Supabase Realtime integration

---

## Architecture Overview

### Tech Stack
- **Frontend**: Next.js 14+ with TypeScript
- **UI Framework**: React 18+
- **Real-time**: Supabase Realtime (WebSocket subscriptions)
- **Styling**: Tailwind CSS
- **State**: React hooks + Context API
- **API**: Supabase JS client for database queries

### Key Components

```
dashboard/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Main dashboard page
│   └── api/
│       └── realtime/
│           └── subscribe.ts    # Realtime subscription handler
├── components/
│   ├── AgentStatus.tsx          # Current agent status card
│   ├── ProposalQueue.tsx         # Pending proposals list
│   ├── BuildProgress.tsx         # Active build progress
│   ├── TaskHistory.tsx           # Recent task history (10 tasks)
│   ├── CostMonitor.tsx           # Daily/monthly cost display
│   └── ApprovalButtons.tsx       # Approve/Reject actions
├── hooks/
│   ├── useRealtimeSubscription.ts  # Supabase realtime subscription
│   └── useAgentStatus.ts           # Agent status fetching
├── lib/
│   ├── supabase.ts              # Supabase client initialization
│   └── utils.ts                 # Helper functions
└── styles/
    └── globals.css              # Global styles
```

---

## Component Specifications

### 1. AgentStatus Component

**Purpose**: Display current agent status and capabilities

**Data Source**:
- Query `nacpac_tasks` (order by `created_at DESC limit 1`)
- Show: current task, status, skillsets loaded, last action

**UI Elements**:
- Status badge (pending/in_progress/completed/failed)
- Current task description
- Skillsets list (7 skills from Phase 1)
- Last action timestamp
- Manual "Start Task" button

**Real-time Updates**: 
- Subscribe to `nacpac_tasks` for status changes
- Update every 5 seconds or on change (whichever comes first)

### 2. ProposalQueue Component

**Purpose**: Show code change proposals awaiting approval

**Data Source**:
- Query `nacpac_tasks` where status = 'proposal_ready'
- Join with feature request details

**UI Elements**:
- Card per proposal with:
  - Feature request description
  - Files to modify count
  - Risks summary
  - "View Diff" button (expands inline diff viewer)
  - "Approve" button (green, calls /api/approve-proposal)
  - "Reject" button (red, calls /api/reject-proposal)

**Real-time Updates**:
- Subscribe to `nacpac_tasks` for proposal_ready status
- Remove card when approved/rejected

### 3. BuildProgress Component

**Purpose**: Display active build progress

**Data Source**:
- Query `nacpac_tasks` where status = 'in_progress' and task_type contains 'build'
- Query `nacpac_runs` for token counts and cost

**UI Elements**:
- Build type badge (APK/EXE)
- Progress bar (estimated % based on elapsed time)
- Elapsed time
- Estimated cost (from Phase 5)
- "Cancel Build" button (if supported)
- Log output (last 10 lines from stderr)

**Real-time Updates**:
- Subscribe to `nacpac_tasks` (in_progress status)
- Update progress every 3 seconds
- Auto-remove when completed

### 4. TaskHistory Component

**Purpose**: Show recent task history and outcomes

**Data Source**:
- Query `nacpac_tasks` order by `created_at DESC limit 10`
- For each task, show status and result

**UI Elements**:
- Table with columns:
  - Task ID (short hash)
  - Created at (relative time)
  - Type (build/deploy/feature)
  - Status (badge color-coded)
  - Result summary (truncated)
  - Cost (from Phase 3 logging)
  - Details button (click to expand)

**Sorting/Filtering**:
- Sort by: created_at (DESC)
- Filter by: status (all/pending/in_progress/completed/failed)

**Real-time Updates**:
- Subscribe to `nacpac_tasks` table
- Add new rows to top as they arrive
- Update status when tasks change

### 5. CostMonitor Component

**Purpose**: Display cost tracking and budget status

**Data Source**:
- Query `nacpac_tasks` for cost_usd sum
- Call RPC functions: `get_daily_cost()`, `get_monthly_cost()`

**UI Elements**:
- Daily cost: $X.XX / $50.00 budget (progress bar)
- Monthly cost: $X.XX / $500.00 budget (progress bar)
- Budget utilization %
- Cost breakdown:
  - By task type (build/deploy/feature)
  - By model (claude-sonnet-5)
- Trend chart (last 7 days daily spend)

**Real-time Updates**:
- Subscribe to `nacpac_tasks` (cost updates)
- Subscribe to `costs` table
- Refresh every 60 seconds

### 6. ApprovalButtons Component (Reusable)

**Purpose**: Handle user approvals for proposals and actions

**Props**:
- `proposal_id`: UUID
- `on_approve`: callback function
- `on_reject`: callback function
- `is_loading`: boolean for button state

**Behavior**:
- POST /api/approve-proposal with proposal_id
- POST /api/reject-proposal with proposal_id
- Show loading spinner during submission
- Show success/error toast notification

---

## Supabase Realtime Subscriptions

### Tables to Subscribe

```typescript
// Subscribe to task status changes
supabase
  .channel('nacpac_tasks')
  .on('postgres_changes', 
    { event: '*', schema: 'public', table: 'nacpac_tasks' },
    (payload) => {
      // Update UI with new task status
    }
  )
  .subscribe();

// Subscribe to run execution logs
supabase
  .channel('nacpac_runs')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'nacpac_runs' },
    (payload) => {
      // Update build progress with new run data
    }
  )
  .subscribe();

// Subscribe to costs
supabase
  .channel('costs')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'costs' },
    (payload) => {
      // Update cost monitor
    }
  )
  .subscribe();
```

---

## API Endpoints (Next.js)

### POST /api/approve-proposal
**Purpose**: Approve a proposal and trigger apply_feature_changes()

**Request**:
```json
{
  "task_id": "uuid",
  "proposal_id": "uuid"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Changes applied on branch feature/...",
  "branch": "feature/...",
  "files_modified": 3
}
```

### POST /api/reject-proposal
**Purpose**: Reject a proposal and update task status

**Request**:
```json
{
  "task_id": "uuid"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Proposal rejected"
}
```

### GET /api/agent-status
**Purpose**: Get current agent status and stats

**Response**:
```json
{
  "status": "ready",
  "current_task": "uuid",
  "skillsets": 7,
  "total_tasks": 42,
  "task_stats": {
    "completed": 35,
    "failed": 2,
    "in_progress": 1
  },
  "daily_cost_usd": 12.50,
  "monthly_cost_usd": 187.30
}
```

---

## Implementation Checklist

### Phase 6a: Setup & Infrastructure
- [ ] Create `dashboard/` directory
- [ ] Initialize Next.js 14 app (npx create-next-app@latest)
- [ ] Configure TypeScript
- [ ] Setup Tailwind CSS
- [ ] Install Supabase client: `npm install @supabase/supabase-js`
- [ ] Create `.env.local` with Supabase credentials

### Phase 6b: Core Components
- [ ] Create `components/` directory
- [ ] Implement AgentStatus component
- [ ] Implement ProposalQueue component
- [ ] Implement BuildProgress component
- [ ] Implement TaskHistory component
- [ ] Implement CostMonitor component
- [ ] Implement ApprovalButtons component (reusable)

### Phase 6c: Realtime Integration
- [ ] Create `lib/supabase.ts` (client initialization)
- [ ] Create `hooks/useRealtimeSubscription.ts`
- [ ] Create `hooks/useAgentStatus.ts`
- [ ] Wire subscriptions into components
- [ ] Test realtime updates with manual task creation

### Phase 6d: API Handlers
- [ ] Create `app/api/approve-proposal.ts`
- [ ] Create `app/api/reject-proposal.ts`
- [ ] Create `app/api/agent-status.ts`
- [ ] Wire approval buttons to API handlers

### Phase 6e: Dashboard Layout
- [ ] Create `app/layout.tsx` with providers
- [ ] Create `app/page.tsx` main dashboard
- [ ] Compose all components
- [ ] Add responsive grid layout
- [ ] Style with Tailwind

### Phase 6f: Testing & Deployment
- [ ] Test all components render correctly
- [ ] Test realtime subscriptions work
- [ ] Test approval flow end-to-end
- [ ] Test on mobile (responsive)
- [ ] Deploy to Vercel

---

## Success Criteria

✅ Dashboard loads and displays agent status  
✅ Real-time updates work (subscribe to tasks, runs, costs)  
✅ Proposal queue shows pending proposals  
✅ Approve/Reject buttons trigger API calls  
✅ Build progress displays estimated ETA and cost  
✅ Task history shows last 10 tasks with cost tracking  
✅ Cost monitor shows daily/monthly budgets  
✅ All components responsive on mobile  
✅ No console errors or warnings  
✅ Dashboard deploys to Vercel  

---

## Future Enhancements (Post-Phase 6)

- [ ] Dark mode toggle
- [ ] Notification toasts for task updates
- [ ] Advanced filtering/sorting in task history
- [ ] Build log viewer (expandable)
- [ ] Skillsets editor (Phase 1 update)
- [ ] Pattern learnings visualization (Phase 2)
- [ ] Performance analytics dashboard
- [ ] Alert configuration (budget, failure rates)
- [ ] Integration with Discord (one-click approve from dashboard)

---

## Notes

- Phase 6 depends on Phases 1-5 being complete
- Realtime subscriptions require Supabase with JWT auth
- Dashboard should work offline (cached data) but refresh when reconnected
- All cost calculations should match Phase 5 logic
- Task IDs should be truncated to first 8 chars in UI

---

**Estimated Implementation Time**: 2-3 days  
**Team Size**: 1 developer  
**Dependencies**: Supabase (realtime enabled), Vercel (hosting)
