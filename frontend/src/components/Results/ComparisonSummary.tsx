import React, { useMemo } from 'react'

type Result = { framework: string, metrics: any }

type Props = { results: Result[] }

export default function ComparisonSummary({ results }: Props) {
  const rows = [
    { fw: 'utilitarian', strength: 'High performance', weakness: 'May favor majority group' },
    { fw: 'fairness', strength: 'Balanced selection', weakness: 'Slightly lower utility' },
    { fw: 'rule_based', strength: 'Enforces constraints', weakness: 'May exclude qualified edge cases' },
  ]
  const color = (fw: string) => fw === 'utilitarian' ? 'badge-green' : fw === 'fairness' ? 'badge-blue' : 'badge-orange'

  // Badge winners
  const winners = useMemo(() => {
    let bestPerf = 'utilitarian', bestPerfVal = -Infinity
    let mostBalanced = 'fairness', mostBalancedVal = -Infinity
    let mostEthical = 'rule_based', mostEthicalVal = -Infinity
    for (const r of results) {
      const fw = r.framework
      const avg = Number(r.metrics?.avg_utility ?? 0)
      const fairness = 1 - Number(r.metrics?.parity_gap ?? 0)
      const constraints = Number(r.metrics?.constraint_satisfaction_rate ?? 0)
      if (avg > bestPerfVal) { bestPerfVal = avg; bestPerf = fw }
      if (fairness > mostBalancedVal) { mostBalancedVal = fairness; mostBalanced = fw }
      if (constraints > mostEthicalVal) { mostEthicalVal = constraints; mostEthical = fw }
    }
    return { bestPerf, mostBalanced, mostEthical }
  }, [results])

  const badge = (label: string, active: boolean, tone: string) => (
    <span className={`badge ${tone} ${active ? '' : 'opacity-40'}`}>{label}</span>
  )

  return (
    <div className="card">
      <div className="card-title">Framework Comparison Summary</div>
      <p className="text-sm text-gray-600 mb-2">Badges mark best frameworks: 🟢 performance, 🟣 fairness balance, 🟠 ethical rule compliance.</p>
      <div className="overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-600">
              <th className="py-2 pr-4">Framework</th>
              <th className="py-2 pr-4">Strength</th>
              <th className="py-2 pr-4">Weakness</th>
              <th className="py-2 pr-4">Badges</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.fw} className="border-t">
                <td className="py-2 pr-4 capitalize">{r.fw.replace('_',' ')}</td>
                <td className="py-2 pr-4">{r.strength}</td>
                <td className="py-2 pr-4">{r.weakness}</td>
                <td className="py-2 pr-4 flex gap-2">
                  {badge('🟢 Best overall performer', winners.bestPerf === r.fw, 'badge-green')}
                  {badge('🟣 Most balanced', winners.mostBalanced === r.fw, 'badge-blue')}
                  {badge('🟠 Most ethical', winners.mostEthical === r.fw, 'badge-orange')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}