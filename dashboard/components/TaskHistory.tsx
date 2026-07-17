// Phase 6: Task History Component
// Displays recent task history with status and cost

import React from 'react'
import { formatRelativeTime, formatCost, getStatusColor } from '@/lib/supabase'

interface Task {
  id: string
  task_input: string
  status: string
  result_summary?: string
  cost_usd?: number
  created_at: string
}

interface TaskHistoryProps {
  tasks: Task[]
}

export function TaskHistory({ tasks }: TaskHistoryProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Recent Tasks (Last 10)</h2>

      {tasks.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No tasks yet</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-4">Task ID</th>
                <th className="text-left py-2 px-4">Created</th>
                <th className="text-left py-2 px-4">Status</th>
                <th className="text-left py-2 px-4">Result</th>
                <th className="text-right py-2 px-4">Cost</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4 font-mono text-xs">
                    {task.id.substring(0, 8)}
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {formatRelativeTime(task.created_at)}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${getStatusColor(task.status)}`}
                    >
                      {task.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-700 truncate max-w-xs">
                    {task.result_summary || '-'}
                  </td>
                  <td className="py-3 px-4 text-right">
                    {task.cost_usd ? formatCost(task.cost_usd) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
