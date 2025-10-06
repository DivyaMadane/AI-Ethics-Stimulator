import React, { useMemo } from 'react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, Title } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend, Title)

type Result = { framework: string, metrics: any }

type Props = { results: Result[], labels?: any }

export default function DonutComparison({ results, labels }: Props) {
  const data = useMemo(() => {
    const perf = Number(results.find(r => r.framework==='utilitarian')?.metrics?.avg_utility ?? 0)
    const fair = 1 - Number(results.find(r => r.framework==='fairness')?.metrics?.parity_gap ?? 1)
    const rule = Number(results.find(r => r.framework==='rule_based')?.metrics?.constraint_satisfaction_rate ?? 0)
    const values = [perf, fair, rule]
    const names = [labels?.utilitarian ?? 'Utilitarian', labels?.fairness ?? 'Fairness', labels?.rule_based ?? 'Rule-based']
    return {
      labels: names,
      datasets: [{
        data: values.map(v => Math.max(0, v)),
        backgroundColor: ['#22c55e','#3b82f6','#f59e0b'],
        borderWidth: 1
      }]
    }
  }, [results, labels])

  if (!results?.length) return null

  return (
    <div className="card">
      <div className="card-title">Framework Share (Key Objective)</div>
      <Doughnut data={data} options={{ plugins: { title: { display: true, text: 'Higher is better' } } }} />
    </div>
  )
}