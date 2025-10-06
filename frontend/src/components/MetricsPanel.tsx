import React from 'react'

type Result = { framework: string, metrics: any, explanation: string }

type Props = { results: Result[] }

export default function MetricsPanel({ results }: Props) {
  if (!results?.length) return null
  return (
    <div className="space-y-4">
      {results.map(r => (
        <div key={r.framework} className="border rounded p-3 bg-white shadow-sm">
          <div className="font-semibold capitalize">{r.framework.replace('_',' ')}</div>
          <pre className="text-xs bg-gray-50 p-2 rounded mt-2 overflow-auto">{JSON.stringify(r.metrics, null, 2)}</pre>
          <div className="text-sm mt-2 text-gray-700">{r.explanation}</div>
        </div>
      ))}
    </div>
  )
}