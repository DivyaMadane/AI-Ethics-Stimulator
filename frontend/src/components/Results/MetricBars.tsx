import React from 'react'

type Props = {
  values: { utilitarian?: number, fairness?: number, rule_based?: number }
  labels?: { utilitarian?: string, fairness?: string, rule_based?: string }
  descriptions?: { utilitarian?: string, fairness?: string, rule_based?: string }
}

const legends = [
  { key: 'utilitarian', label: 'Utilitarian (Performance)', color: 'bg-green-500', explain: 'Utilitarian focuses on maximizing overall performance.' },
  { key: 'fairness', label: 'Fairness (Balance)', color: 'bg-blue-500', explain: 'Fairness reflects balance across protected groups (higher is more equal).' },
  { key: 'rule_based', label: 'Rule-based (Constraints)', color: 'bg-orange-500', explain: 'Rule-based enforces hard constraints or ethical rules.' },
] as const

export default function MetricBars({ values, labels, descriptions }: Props) {
  const fmt = (v?: number) => Math.max(0, Math.min(1, Number(v ?? 0))).toFixed(2)
  return (
    <div className="space-y-3">
      {legends.map(l => {
        const v = Math.max(0, Math.min(1, Number(values[l.key as keyof typeof values] ?? 0)))
        return (
          <div key={l.key} className="card">
            <div className="flex items-center justify-between">
              <div className="font-medium flex items-center gap-2">
                <span className="text-xl">{l.key === 'fairness' ? '⚖️' : l.key === 'utilitarian' ? '📈' : '🧭'}</span>
                <span>{labels?.[l.key] ?? l.label}</span>
              </div>
              <div className="text-sm text-gray-600" title={descriptions?.[l.key] ?? l.explain}>{Math.round(v*100)}%</div>
            </div>
            <div className="w-full h-3 bg-gray-100 rounded mt-2 overflow-hidden">
              <div className={`h-3 rounded ${l.color} transition-all duration-500`} style={{ width: `${v*100}%` }}></div>
            </div>
          </div>
        )
      })}
      <div className="text-sm text-gray-700 mt-2">
        <p>• Higher Fairness means equal opportunity across candidates.</p>
        <p>• Utilitarian focuses on overall performance.</p>
        <p>• Rule-based enforces constraints or ethical rules.</p>
      </div>
    </div>
  )
}