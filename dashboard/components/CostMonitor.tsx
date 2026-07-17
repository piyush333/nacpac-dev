// Phase 6: Cost Monitor Component
// Displays daily and monthly budget tracking

import React from 'react'
import { formatCost } from '@/lib/supabase'

interface CostMonitorProps {
  dailyCost: number
  dailyBudget: number
  monthlyCost: number
  monthlyBudget: number
}

function ProgressBar({
  current,
  max,
  label,
}: {
  current: number
  max: number
  label: string
}) {
  const percentage = Math.min((current / max) * 100, 100)
  const isOverBudget = current > max

  return (
    <div className="mb-6">
      <div className="flex justify-between mb-2">
        <span className="font-medium">{label}</span>
        <span className={isOverBudget ? 'text-red-600 font-bold' : ''}>
          {formatCost(current)} / {formatCost(max)}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all ${
            isOverBudget
              ? 'bg-red-500'
              : percentage > 80
                ? 'bg-yellow-500'
                : 'bg-green-500'
          }`}
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
      <p className="text-xs text-gray-500 mt-1">
        {percentage.toFixed(0)}% of budget used
      </p>
    </div>
  )
}

export function CostMonitor({
  dailyCost,
  dailyBudget,
  monthlyCost,
  monthlyBudget,
}: CostMonitorProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-6">Cost Monitor</h2>

      <ProgressBar
        current={dailyCost}
        max={dailyBudget}
        label="Daily Budget"
      />

      <ProgressBar
        current={monthlyCost}
        max={monthlyBudget}
        label="Monthly Budget"
      />

      {dailyCost > dailyBudget && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          ⚠️ Daily budget exceeded by {formatCost(dailyCost - dailyBudget)}
        </div>
      )}

      {monthlyCost > monthlyBudget && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          ⚠️ Monthly budget exceeded by {formatCost(monthlyCost - monthlyBudget)}
        </div>
      )}
    </div>
  )
}
