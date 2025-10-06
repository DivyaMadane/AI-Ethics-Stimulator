import React, { useEffect, useMemo, useState } from 'react'
import { getScenarios } from '../services/api'

type Scenario = { id: number, name: string, type: string, config?: any }

type Props = {
  selected: number | null
  onSelect: (id: number) => void
  params: any
  setParams: (p: any) => void
  frameworks: Record<string, boolean>
  setFrameworks: (f: Record<string, boolean>) => void
  displayLabels?: { utilitarian?: string, fairness?: string, rule_based?: string }
}

function titleCase(s: string) {
  return s.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export default function ScenarioConfigurator({ selected, onSelect, params, setParams, frameworks, setFrameworks, displayLabels }: Props) {
  const [scenarios, setScenarios] = useState<Scenario[]>([])

  useEffect(() => {
    getScenarios()
      .then((list) => {
        // Exclude seeded demo
        setScenarios(list.filter((s: any) => s.name !== 'Hiring Bias Demo'))
      })
      .catch(console.error)
  }, [])

  const selectedScenario = useMemo(() => scenarios.find(s => s.id === selected) ?? null, [scenarios, selected])

  // Initialize params from selected scenario's default_params when selection changes
  useEffect(() => {
    if (!selectedScenario) return
    const def = selectedScenario.config?.default_params ?? {}
    const utilKeys: string[] = selectedScenario.config?.metrics?.utility_features ?? []
    const baseWeights: Record<string, number> = Object.fromEntries(utilKeys.map(k => [k, 0.5]))
    const desiredWeights = { ...baseWeights, ...(def.weights ?? {}) }

    // Initialize if weights are missing or incomplete, and ensure top_k exists
    const hasAllWeights = params?.weights && Object.keys(desiredWeights).every(k => k in (params.weights || {}))
    if (!hasAllWeights) {
      setParams({ top_k: params?.top_k ?? def.top_k ?? 10, weights: { ...desiredWeights } })
    } else if (typeof params?.top_k !== 'number') {
      setParams({ ...params, top_k: def.top_k ?? 10 })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedScenario?.id])

  // Determine which weight fields to render and their current values
  const weightEntries: [string, number][] = useMemo(() => {
    const utilKeys: string[] = selectedScenario?.config?.metrics?.utility_features ?? []
    const defWeights = selectedScenario?.config?.default_params?.weights ?? {}

    const allKeys = Array.from(new Set([
      ...Object.keys(defWeights || {}),
      ...Object.keys((params?.weights) || {}),
      ...utilKeys,
    ]))

    return allKeys.map((k) => [k, Number((params?.weights?.[k] ?? defWeights?.[k] ?? (utilKeys.includes(k) ? 0.5 : 0)))]) as [string, number][]
  }, [params?.weights, selectedScenario])

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Scenario</label>
        <select className="mt-1 w-full border rounded p-2" value={selected ?? ''} onChange={e => onSelect(Number(e.target.value))}>
          <option value="" disabled>Select scenario</option>
          {scenarios.map(s => <option key={s.id} value={s.id}>{s.name} ({s.type})</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium">Top K</label>
          <input type="range" min={1} max={50} className="mt-2 w-full" value={params.top_k ?? 10}
            onChange={e => setParams({ ...params, top_k: Number(e.target.value) })} />
          <div className="text-xs text-gray-600">{params.top_k ?? 10}</div>
        </div>

        {weightEntries.map(([key, val]) => (
          <div key={key}>
            <label className="block text-sm font-medium">Weight: {titleCase(key)}</label>
            <input
              type="range"
              min={-1}
              max={1}
              step={0.05}
              className="mt-2 w-full"
              value={val}
              onChange={e => setParams({ ...params, weights: { ...params.weights, [key]: Number(e.target.value) } })}
            />
            <div className="text-xs text-gray-600">{Number(val).toFixed(2)}</div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-sm text-gray-700 bg-blue-50 border border-blue-100 rounded p-3">
        <div><span className="font-semibold">Scenario:</span> {selectedScenario ? `${selectedScenario.name} (${selectedScenario.type})` : '—'}</div>
        <div><span className="font-semibold">Top K:</span> {params.top_k ?? 10}</div>
        {weightEntries.length > 0 && (
          <div>
            <span className="font-semibold">Weights:</span> {weightEntries.map(([k, v]) => `${titleCase(k)}=${Number(v).toFixed(2)}`).join(' · ')}
          </div>
        )}
        <div><span className="font-semibold">Frameworks Compared:</span> Utilitarian, Fairness, Rule-based</div>
      </div>

      <div>
        <label className="block text-sm font-medium">Frameworks</label>
        <div className="mt-1 flex gap-4">
          {['utilitarian','fairness','rule_based'].map(key => (
            <label key={key} className="inline-flex items-center gap-2">
              <input type="checkbox" checked={frameworks[key]} onChange={e => setFrameworks({ ...frameworks, [key]: e.target.checked })} />
              <span className="capitalize">{(typeof (displayLabels as any)?.[key] === 'string') ? (displayLabels as any)[key] : key.replace('_',' ')}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  )
}
