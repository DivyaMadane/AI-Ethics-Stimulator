import React from 'react'

type Props = {
  scenarioType?: string
  values: { utilitarian?: number, fairness?: number, rule_based?: number }
  comparison?: any
}

export default function NarrativeSummary({ scenarioType, values, comparison }: Props) {
  const perf = Math.round((values.utilitarian ?? 0) * 100)
  const fair = Math.round((values.fairness ?? 0) * 100)
  const rule = Math.round((values.rule_based ?? 1) * 100)
  const lines: string[] = []
  if (scenarioType === 'healthcare') {
    lines.push(`Accuracy is ${perf}%. Patient Safety ${rule}%. Bias Mitigation ${fair}%.`)
  } else if (scenarioType === 'self_driving') {
    lines.push(`Safety Score is ${perf}%. Ethical Balance ${fair}%. Law Compliance ${rule}%.`)
  } else {
    lines.push(`Performance is ${perf}%. Fairness ${fair}%. Rule Compliance ${rule}%.`)
  }
  if (comparison?.text?.length) {
    lines.push(...comparison.text)
  }
  return (
    <div className="text-sm text-gray-700 space-y-1">
      {lines.map((t, i) => <div key={i}>• {t}</div>)}
    </div>
  )
}