// Phase 6: Agent Status Component
// Displays current agent status and skillsets

import React from 'react'
import { formatRelativeTime } from '@/lib/supabase'

interface AgentStatusProps {
  currentTask?: string
  status: string
  skillsetsLoaded: number
  lastAction?: string
}

export function AgentStatus({
  currentTask,
  status,
  skillsetsLoaded,
  lastAction,
}: AgentStatusProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Agent Status</h2>

      {/* Status Badge */}
      <div className="mb-4">
        <span
          className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
            status === 'ready'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {status === 'ready' ? '🟢 Ready' : '🟡 Busy'}
        </span>
      </div>

      {/* Current Task */}
      {currentTask && (
        <div className="mb-4">
          <p className="text-gray-600 text-sm">Current Task</p>
          <p className="font-mono text-sm truncate">{currentTask}</p>
        </div>
      )}

      {/* Skillsets */}
      <div className="mb-4">
        <p className="text-gray-600 text-sm">Skillsets Loaded</p>
        <p className="text-lg font-semibold">{skillsetsLoaded}/7</p>
      </div>

      {/* Last Action */}
      {lastAction && (
        <div className="text-gray-500 text-xs">
          Last action: {formatRelativeTime(lastAction)}
        </div>
      )}

      {/* Start Task Button */}
      <button className="mt-4 w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        + Start New Task
      </button>
    </div>
  )
}
