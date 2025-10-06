import React, { useEffect, useMemo, useState } from 'react'
import ScenarioConfigurator from './components/ScenarioConfigurator'
import MetricsPanel from './components/MetricsPanel'
import TradeoffChart from './components/Charts/TradeoffChart'
import MetricBars from './components/Results/MetricBars'
import SelectedTable from './components/Results/SelectedTable'
import ComparisonSummary from './components/Results/ComparisonSummary'
import KpiStrip from './components/Results/KpiStrip'
import RecordsTable from './components/Results/RecordsTable'
import NarrativeSummary from './components/Results/NarrativeSummary'
import { simulate, getScenario } from './services/api'
// @ts-ignore
import confetti from 'canvas-confetti'

function App() {
  const [scenarioId, setScenarioId] = useState<number | null>(null)
  const [scenarioDetails, setScenarioDetails] = useState<any | null>(null)
  const [params, setParams] = useState<any>({ top_k: 10, weights: { experience: 0.5, test_score: 0.5 } })
  const [frameworks, setFrameworks] = useState({ utilitarian: true, fairness: true, rule_based: true })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [labels, setLabels] = useState<any>({})
  const [descriptions, setDescriptions] = useState<any>({})
  const [comparison, setComparison] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!scenarioId) { setScenarioDetails(null); return }
    getScenario(scenarioId).then(setScenarioDetails).catch(console.error)
  }, [scenarioId])

  const selectedFrameworks = useMemo(() => Object.entries(frameworks).filter(([_,v]) => v).map(([k,_]) => k), [frameworks])

  const run = async () => {
    if (!scenarioId) { setError('Please select a scenario.'); return }
    setLoading(true)
    setError(null)
    try {
      const resp = await simulate({ scenario_id: scenarioId, frameworks: selectedFrameworks, params })
      setResults(resp.run.results)
      setLabels(resp.labels || {})
      setDescriptions(resp.descriptions || {})
      setComparison(resp.comparison || null)
    } catch (e:any) {
      setError(e.message)
    } finally {
      setLoading(false)
      try { confetti({ particleCount: 60, spread: 60, origin: { y: 0.6 } }) } catch {}
    }
  }

  // Build metric bar inputs
  const metricValues = useMemo(() => {
    const m: any = {}
    for (const r of results) {
      if (r.framework === 'utilitarian') m.utilitarian = Number(r.metrics?.total_utility ?? 0) / Math.max(1, Number(params.top_k || 1))
      if (r.framework === 'fairness') m.fairness = 1 - (Number(r.metrics?.parity_gap ?? 0))
      if (r.framework === 'rule_based') m.rule_based = Number(r.metrics?.constraint_satisfaction_rate ?? 1)
    }
    return m
  }, [results, params])

  // Build selected sets per framework
  const selectedSets = useMemo(() => {
    const map: Record<string, Set<string>> = { utilitarian: new Set(), fairness: new Set(), rule_based: new Set() }
    for (const r of results) {
      const ids: string[] = r?.decisions?.selected_ids || []
      for (const id of ids) map[r.framework]?.add(String(id))
    }
    return map
  }, [results])

  const entitiesById: Record<string, any> = useMemo(() => {
    const rec: Record<string, any> = {}
    const entities = scenarioDetails?.config?.entities || []
    for (const e of entities) rec[String(e.id)] = e
    return rec
  }, [scenarioDetails])

  return (
    <div className="min-h-screen">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <header className="text-center">
          <h1 className="text-3xl font-bold">AI Ethics Simulator — Hiring Decision Dashboard</h1>
          <p className="text-gray-700 mt-1">Compare utilitarian, fairness-aware, and rule-based outcomes on realistic hiring data.</p>
        </header>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="card">
            <div className="card-title">Configuration</div>
            <ScenarioConfigurator selected={scenarioId} onSelect={setScenarioId}
              params={params} setParams={setParams}
              frameworks={frameworks} setFrameworks={setFrameworks}
              displayLabels={labels}
            />
            <div className="flex items-center gap-3 mt-4">
              <button onClick={run} disabled={loading} className="button-primary disabled:opacity-50">
                {loading ? 'Running...' : 'Run Simulation'}
              </button>
              <button onClick={run} disabled={loading || !results.length} className="px-4 py-2 rounded-md bg-gray-100 text-gray-800 hover:bg-gray-200 transition">
                Re-run Simulation
              </button>
              <button onClick={() => {
                // Export current results to CSV
                const rows: string[] = []
                rows.push(['framework','metric','value'].join(','))
                for (const r of results) {
                  const m = r.metrics || {}
                  for (const k of Object.keys(m)) {
                    rows.push([r.framework, k, String(m[k])].join(','))
                  }
                }
                const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'simulation_results.csv'
                a.click()
                URL.revokeObjectURL(url)
              }} disabled={!results.length} className="px-4 py-2 rounded-md bg-green-50 text-green-700 hover:bg-green-100 transition">
                Export Results (CSV)
              </button>
              {error && <div className="text-red-600 text-sm">{error}</div>}
            </div>
          </div>

          <div className="card">
            <div className="card-title">Key Metrics</div>
            <MetricBars values={metricValues} labels={labels} descriptions={descriptions} />
            {comparison?.text?.length ? (
              <div className="text-xs text-gray-600 mt-2 space-y-1">
                {comparison.text.map((t: string, i: number) => (<div key={i}>• {t}</div>))}
              </div>
            ) : null}
          </div>
        </div>

        <div className="card">
          <div className="card-title">Trade-off Chart</div>
          <TradeoffChart results={results} />
        </div>

        <KpiStrip results={results} labels={labels} />
        <ComparisonSummary results={results} />
        <div className="card">
          <div className="card-title">Summary Insight</div>
          <p className="text-sm text-gray-700">{
            (() => {
              const perf = results.find(r => r.framework==='utilitarian')?.metrics?.avg_utility ?? 0
              const fair = 1 - (results.find(r => r.framework==='fairness')?.metrics?.parity_gap ?? 1)
              const rule = results.find(r => r.framework==='rule_based')?.metrics?.constraint_satisfaction_rate ?? 0
              const bestVal = Math.max(perf, fair, rule)
              const best = bestVal === perf ? 'Utilitarian' : bestVal === fair ? 'Fairness' : 'Rule-based'
              return `Best Decision Framework: ${best} (${Math.round((bestVal)*100)}% on its key objective)`
            })()
          }</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="card">
            <div className="card-title">Metrics & Explanations</div>
            <MetricsPanel results={results} />
            <div className="mt-3">
              <NarrativeSummary scenarioType={scenarioDetails?.config?.type} values={metricValues} comparison={comparison} />
            </div>
          </div>

          {scenarioDetails?.config?.type === 'hiring' ? (
            <SelectedTable entitiesById={entitiesById} selected={selectedSets} limit={Math.max(10, Number(params.top_k || 10))} />
          ) : null}
        </div>

        <RecordsTable scenarioType={scenarioDetails?.config?.type} entities={scenarioDetails?.config?.entities || []} selectedIds={new Set(Array.from(selectedSets.utilitarian ?? new Set()))} />
      </div>
    </div>
  )
}

export default App
