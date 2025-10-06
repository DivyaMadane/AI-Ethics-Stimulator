import React from 'react'

type Props = {
  scenarioType?: string
  entities: any[]
  selectedIds: Set<string>
  limit?: number
}

export default function RecordsTable({ scenarioType, entities, selectedIds, limit = 20 }: Props) {
  const [showAll, setShowAll] = React.useState(false)
  const cols = React.useMemo(() => {
    if (scenarioType === 'healthcare') return ['id','age','severity','priority','income_group']
    if (scenarioType === 'self_driving') return ['id','passenger_age','pedestrian_age','risk_level','group']
    return ['id','name','gender','department','experience','test_score']
  }, [scenarioType])
  const rows = React.useMemo(() => (showAll ? entities : entities.slice(0, limit)), [entities, showAll, limit])
  if (!entities?.length) return null
  return (
    <div className="card">
      <div className="card-title">Records Preview</div>
      <div className="flex items-center justify-between mb-2">
        <div className="text-sm text-gray-600">Showing {showAll ? entities.length : Math.min(limit, entities.length)} of {entities.length} records</div>
        <button className="px-3 py-1 rounded bg-gray-100 hover:bg-gray-200" onClick={() => setShowAll(s => !s)}>
          {showAll ? 'Show Less' : 'Show All'}
        </button>
      </div>
      <div className="overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-600">
              {cols.map(c => <th key={c} className="py-2 pr-4 capitalize">{c.replace('_',' ')}</th>)}
              <th className="py-2 pr-4">Selected?</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((e, idx) => (
              <tr key={e.id ?? idx} className="border-t">
                {cols.map(c => <td key={c} className="py-2 pr-4">{e[c] ?? '-'}</td>)}
                <td className="py-2 pr-4">{selectedIds.has(String(e.id)) ? '✅' : ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}