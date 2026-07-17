// Phase 6: Main Dashboard Page
// Composes all dashboard components with realtime updates

'use client'

import React, { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import { AgentStatus } from '@/components/AgentStatus'
import { TaskHistory } from '@/components/TaskHistory'
import { CostMonitor } from '@/components/CostMonitor'

interface Task {
  id: string
  agent_id: string
  task_input: string
  status: string
  result_summary?: string
  cost_usd?: number
  created_at: string
  completed_at?: string
}

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [dailyCost, setDailyCost] = useState(0)
  const [monthlyCost, setMonthlyCost] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Fetch initial data
  useEffect(() => {
    fetchTasks()
    fetchCosts()
  }, [])

  // Subscribe to realtime updates
  useEffect(() => {
    const subscription = supabase
      .channel('nacpac_tasks')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'nacpac_tasks' },
        (payload) => {
          console.log('Task update:', payload)
          fetchTasks()
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  async function fetchTasks() {
    try {
      setLoading(true)
      const { data, error } = await supabase
        .from('nacpac_tasks')
        .select('*')
        .eq('agent_id', 'nacpac_dev')
        .order('created_at', { ascending: false })
        .limit(10)

      if (error) throw error
      setTasks(data || [])
      setError(null)
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
      setError(
        err instanceof Error ? err.message : 'Failed to load tasks'
      )
    } finally {
      setLoading(false)
    }
  }

  async function fetchCosts() {
    try {
      // Fetch daily cost
      const today = new Date().toISOString().split('T')[0]
      const { data: dailyData } = await supabase
        .from('nacpac_tasks')
        .select('cost_usd')
        .eq('agent_id', 'nacpac_dev')
        .filter('created_at', 'gte', `${today}T00:00:00`)

      const daily = (dailyData || []).reduce(
        (sum, task) => sum + (task.cost_usd || 0),
        0
      )
      setDailyCost(daily)

      // Fetch monthly cost
      const monthStart = new Date()
      monthStart.setDate(1)
      const monthStartStr = monthStart.toISOString().split('T')[0]
      const { data: monthlyData } = await supabase
        .from('nacpac_tasks')
        .select('cost_usd')
        .eq('agent_id', 'nacpac_dev')
        .filter('created_at', 'gte', `${monthStartStr}T00:00:00`)

      const monthly = (monthlyData || []).reduce(
        (sum, task) => sum + (task.cost_usd || 0),
        0
      )
      setMonthlyCost(monthly)
    } catch (err) {
      console.error('Failed to fetch costs:', err)
    }
  }

  const currentTask = tasks.find((t) => t.status === 'in_progress')
  const completedCount = tasks.filter((t) => t.status === 'completed').length
  const failedCount = tasks.filter((t) => t.status === 'failed').length

  return (
    <div className="space-y-8">
      {/* Error Banner */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          ⚠️ {error}
        </div>
      )}

      {/* Top Row: Status, Cost, Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <AgentStatus
          currentTask={currentTask?.task_input}
          status={currentTask ? 'busy' : 'ready'}
          skillsetsLoaded={7}
          lastAction={tasks[0]?.created_at}
        />

        <CostMonitor
          dailyCost={dailyCost}
          dailyBudget={50}
          monthlyCost={monthlyCost}
          monthlyBudget={500}
        />

        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
          <div className="space-y-3">
            <div>
              <p className="text-gray-600 text-sm">Total Tasks</p>
              <p className="text-2xl font-bold">{tasks.length}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Completed</p>
              <p className="text-xl font-semibold text-green-600">
                {completedCount}
              </p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Failed</p>
              <p className="text-xl font-semibold text-red-600">
                {failedCount}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Task History */}
      <TaskHistory tasks={tasks} />

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      )}
    </div>
  )
}
