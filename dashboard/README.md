# NacPac Dev Agent Dashboard (Phase 6)

Real-time dashboard for monitoring and controlling the NacPac Dev Agent.

## Features

- 🟢 **Agent Status**: Current status, skillsets, and active tasks
- 📊 **Cost Monitoring**: Daily and monthly budget tracking
- 📋 **Task History**: Last 10 tasks with status and costs
- 🔄 **Real-time Updates**: Supabase realtime subscriptions
- 🎛️ **Proposal Management**: Approve/reject code change proposals
- 📈 **Build Progress**: Track active builds with ETA and cost

## Tech Stack

- **Framework**: Next.js 14 with React 18
- **Database**: Supabase with realtime subscriptions
- **Styling**: Tailwind CSS
- **Language**: TypeScript

## Getting Started

### Prerequisites

- Node.js 18+
- Supabase project with JWT auth enabled
- NacPac Dev Agent running (Phases 1-5 complete)

### Installation

```bash
# Install dependencies
npm install

# Create .env.local from .env.example
cp .env.example .env.local

# Fill in your Supabase credentials
# NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Development

```bash
# Start dev server
npm run dev

# Open http://localhost:3000 in browser
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
dashboard/
├── app/
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Main dashboard page
│   ├── api/                 # API handlers
│   │   ├── approve-proposal.ts
│   │   ├── reject-proposal.ts
│   │   └── agent-status.ts
├── components/
│   ├── AgentStatus.tsx       # Status display
│   ├── TaskHistory.tsx       # Recent tasks table
│   ├── CostMonitor.tsx       # Budget tracking
│   ├── ProposalQueue.tsx     # Pending proposals
│   ├── BuildProgress.tsx     # Active build tracking
│   └── ApprovalButtons.tsx   # Reusable approval UI
├── hooks/
│   ├── useRealtimeSubscription.ts  # Supabase subscriptions
│   └── useAgentStatus.ts           # Status fetching
├── lib/
│   ├── supabase.ts           # Supabase client
│   └── utils.ts              # Helper functions
├── styles/
│   └── globals.css           # Tailwind CSS
├── package.json
├── tsconfig.json
├── next.config.js
└── README.md
```

## Components

### AgentStatus
Displays current agent status, active task, and skillsets loaded.

**Data**: Queries `nacpac_tasks` for latest status

### TaskHistory
Shows last 10 tasks with status and cost tracking.

**Data**: Subscribes to `nacpac_tasks` realtime updates

### CostMonitor
Displays daily and monthly budget usage with progress bars.

**Data**: Aggregates cost from `nacpac_tasks` table

### ProposalQueue
Lists pending code change proposals awaiting approval.

**Data**: Filters `nacpac_tasks` for `status = 'proposal_ready'`

### BuildProgress
Tracks active builds with ETA and estimated cost.

**Data**: Subscribes to `nacpac_tasks` and `nacpac_runs`

## Realtime Subscriptions

Dashboard subscribes to:

1. **nacpac_tasks** - Task creation, status changes, completion
2. **nacpac_runs** - Execution logs with token counts and costs
3. **costs** - API call cost tracking

Updates are received instantly via WebSocket connection.

## API Endpoints

### POST /api/approve-proposal
Approve a proposal and trigger apply_feature_changes()

### POST /api/reject-proposal
Reject a proposal and update task status

### GET /api/agent-status
Get current agent status and statistics

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | Supabase anonymous key |
| `NEXT_PUBLIC_API_URL` | No | API base URL (default: /api) |

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Add environment variables in Vercel dashboard
```

### Docker

```bash
# Build image
docker build -t nacpac-dashboard .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_SUPABASE_URL=... \
  -e NEXT_PUBLIC_SUPABASE_ANON_KEY=... \
  nacpac-dashboard
```

## Testing

Dashboard components can be tested with:

```bash
# Run tests (when test setup is added)
npm run test

# Check types
npm run type-check

# Lint code
npm run lint
```

## Troubleshooting

### Realtime Updates Not Working
- Check Supabase project has realtime enabled
- Verify JWT auth is configured
- Check browser console for WebSocket errors

### Build Errors
- Ensure Node.js 18+: `node --version`
- Clear cache: `rm -rf .next node_modules && npm install`
- Check TypeScript: `npm run type-check`

### Cost Data Not Showing
- Verify `nacpac_tasks` table has cost_usd values
- Check Supabase credentials in .env.local
- Manually trigger a task to populate data

## Contributing

Dashboard follows the NacPac Dev Agent development standards:

- TypeScript for type safety
- Tailwind CSS for styling
- Realtime Supabase for data sync
- React hooks for state management

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Notification toasts
- [ ] Advanced filtering/sorting
- [ ] Build log viewer
- [ ] Performance analytics
- [ ] Alert configuration
- [ ] Discord integration

## License

Part of NacPac Dev Agent (Phases 1-8)

---

**Next Phase**: Phase 7: Testing - Comprehensive test suite and validation
