export interface SimulatePayload {
  scenario_id?: number
  scenario_inline?: any
  frameworks: string[]
  params: Record<string, any>
}

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

export async function getScenarios() {
  const res = await fetch(`${API_BASE}/scenarios`)
  if (!res.ok) throw new Error('Failed to load scenarios')
  return res.json()
}

export async function getScenario(id: number) {
  const res = await fetch(`${API_BASE}/scenarios/${id}`)
  if (!res.ok) throw new Error('Failed to load scenario')
  return res.json()
}

export async function simulate(payload: SimulatePayload) {
  const res = await fetch(`${API_BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  if (!res.ok) throw new Error('Simulation failed')
  return res.json()
}
