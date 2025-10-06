import React, { useMemo } from 'react'

type Props = { results: any[], labels?: any }

export default function KpiStrip({ results, labels }: Props) {
  const vals = useMemo(() => {
    const perf = Number(results.find(r => r.framework==='utilitarian')?.metrics?.avg_utility ?? 0)
    const fair = 1 - Number(results.find(r => r.framework==='fairness')?.metrics?.parity_gap ?? 1)
    const rule = Number(results.find(r => r.framework==='rule_based')?.metrics?.constraint_satisfaction_rate ?? 0)
    return [
      { key: 'utilitarian', label: labels?.utilitarian ?? 'Utilitarian', value: perf, color: 'text-green-600', bg: 'bg-green-50' },
      { key: 'fairness', label: labels?.fairness ?? 'Fairness', value: fair, color: 'text-blue-600', bg: 'bg-blue-50' },
      { key: 'rule_based', label: labels?.rule_based ?? 'Rule-based', value: rule, color: 'text-orange-600', bg: 'bg-orange-50' },
    ]
  }, [results, labels])

  if (!results?.length) return null

  return (
    <div className="grid sm:grid-cols-3 gap-3">
      {vals.map(v => (
        <div key={v.key} className={`rounded-lg p-3 ${v.bg}`}>
          <div className="text-xs text-gray-600">{v.label}</div>
          <div className={`text-2xl font-semibold ${v.color}`}>{Math.round(v.value*100)}%</div>
        </div>
      ))}
    </div>
  )
}