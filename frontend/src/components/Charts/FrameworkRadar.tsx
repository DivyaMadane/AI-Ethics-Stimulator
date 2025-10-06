// Deprecated in favor of DonutComparison; keeping file for reference if needed
export default function FrameworkRadar() { return null }

import React, { useMemo } from 'react'
import { Radar } from 'react-chartjs-2'
import { Chart as ChartJS, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend } from 'chart.js'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

type Result = { framework: string, metrics: any }

type Props = { results: Result[] }

export default function FrameworkRadar({ results }: Props) {
  const data = useMemo(() => {
    const labels = ['Performance (Avg Utility)', 'Fairness (1 - Parity Gap)', 'Constraints (Satisfaction)']
    const fwMap: Record<string, [number, number, number]> = {}
    for (const r of results) {
      const avg = Number(r.metrics?.avg_utility ?? 0)
      const fair = 1 - Number(r.metrics?.parity_gap ?? 0)
      const cons = Number(r.metrics?.constraint_satisfaction_rate ?? 0)
      fwMap[r.framework] = [avg, fair, cons]
    }
    const c = (fw: string) => fw === 'utilitarian' ? 'rgba(34,197,94,0.5)' : fw === 'fairness' ? 'rgba(59,130,246,0.5)' : 'rgba(245,158,11,0.5)'
    const border = (fw: string) => fw === 'utilitarian' ? 'rgba(34,197,94,1)' : fw === 'fairness' ? 'rgba(59,130,246,1)' : 'rgba(245,158,11,1)'

    return {
      labels,
      datasets: Object.entries(fwMap).map(([fw, arr]) => ({
        label: fw,
        data: arr,
        backgroundColor: c(fw),
        borderColor: border(fw),
        borderWidth: 2,
        pointBackgroundColor: border(fw),
      }))
    }
  }, [results])

  if (!results?.length) return null

  return (
    <div className="card">
      <div className="card-title">Radar Comparison</div>
      <Radar data={data} options={{ plugins: { title: { display: true, text: 'Framework Radar' }, legend: { display: true } }, scales: { r: { suggestedMin: 0, suggestedMax: 1 } } }} />
    </div>
  )
}