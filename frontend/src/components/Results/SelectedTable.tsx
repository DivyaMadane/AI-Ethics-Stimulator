import React from 'react'

type Entity = { id: string, name?: string, experience?: number, test_score?: number, gender?: string, department?: string }

type Props = {
  entitiesById: Record<string, Entity>
  selected: Record<string, Set<string>> // framework -> set of ids
  limit?: number
}

export default function SelectedTable({ entitiesById, selected, limit = 15 }: Props) {
  const frameworks = ['utilitarian','fairness','rule_based']
  const [sortKey, setSortKey] = React.useState<keyof Entity | 'id'>('id')
  const [sortDir, setSortDir] = React.useState<'asc'|'desc'>('asc')
  const unionIds = Array.from(new Set(Array.from(frameworks.flatMap(f => Array.from(selected[f] ?? new Set())))))

  const sorted = React.useMemo(() => {
    const arr = [...unionIds]
    const cmp = (a: string, b: string) => {
      const va: any = entitiesById[a]?.[sortKey]
      const vb: any = entitiesById[b]?.[sortKey]
      const na = (typeof va === 'number') ? va : String(va ?? '').toLowerCase()
      const nb = (typeof vb === 'number') ? vb : String(vb ?? '').toLowerCase()
      if (na < nb) return sortDir === 'asc' ? -1 : 1
      if (na > nb) return sortDir === 'asc' ? 1 : -1
      return 0
    }
    arr.sort(cmp)
    return arr.slice(0, limit)
  }, [unionIds, entitiesById, sortKey, sortDir, limit])

  if (!sorted.length) return null

  const cell = (fw: string, id: string) => (selected[fw]?.has(id) ? '✅' : '')

  const header = (key: keyof Entity | 'id', label: string) => (
    <th className="py-2 pr-4 cursor-pointer hover:text-gray-900" onClick={() => { setSortKey(key); setSortDir(d => d === 'asc' ? 'desc' : 'asc') }}>
      {label}{sortKey === key ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''}
    </th>
  )

  return (
    <div className="card">
      <div className="card-title">Top Selected Candidates</div>
      <div className="overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-600">
              <th className="py-2 pr-4">Candidate</th>
              <th className="py-2 pr-4">Gender</th>
              <th className="py-2 pr-4">Dept</th>
              <th className="py-2 pr-4">Experience</th>
              <th className="py-2 pr-4">Test Score</th>
              <th className="py-2 pr-4 text-green-700">Utilitarian</th>
              <th className="py-2 pr-4 text-blue-700">Fairness</th>
              <th className="py-2 pr-4 text-orange-700">Rule-based</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(id => {
              const e = entitiesById[id] || { id }
              return (
                <tr key={id} className="border-t">
                  <td className="py-2 pr-4 font-medium">{e.name ?? id}</td>
                  <td className="py-2 pr-4">{e.gender ?? '-'}</td>
                  <td className="py-2 pr-4">{e.department ?? '-'}</td>
                  <td className="py-2 pr-4">{e.experience ?? '-'}</td>
                  <td className="py-2 pr-4">{e.test_score ?? '-'}</td>
                  <td className="py-2 pr-4">{cell('utilitarian', id)}</td>
                  <td className="py-2 pr-4">{cell('fairness', id)}</td>
                  <td className="py-2 pr-4">{cell('rule_based', id)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}