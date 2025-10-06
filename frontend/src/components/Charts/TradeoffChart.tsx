import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'

type Result = { framework: string, metrics: any }

type Props = { results: Result[] }

export default function TradeoffChart({ results }: Props) {
  const ref = useRef<SVGSVGElement | null>(null)

  useEffect(() => {
    if (!ref.current) return
    const svg = d3.select(ref.current)
    svg.selectAll('*').remove()

    const width = 500, height = 260, margin = { top: 20, right: 20, bottom: 40, left: 50 }
    const g = svg.attr('viewBox', `0 0 ${width} ${height}`).append('g').attr('transform', `translate(${margin.left},${margin.top})`)

    const data = results.map(r => {
      const fw = r.framework as string
      let value = 0
      if (fw === 'utilitarian') {
        const v = r?.metrics?.total_utility
        value = Number.isFinite(v) ? Number(v) : 0
      } else if (fw === 'fairness') {
        const gap = r?.metrics?.parity_gap
        const mapped = 1 - (Number.isFinite(gap) ? Number(gap) : 0)
        value = Number.isFinite(mapped) ? mapped : 0
      } else if (fw === 'rule_based') {
        // Default to 1 if undefined, then coerce to number
        const v = r?.metrics?.constraint_satisfaction_rate
        value = Number.isFinite(v) ? Number(v) : 1
      } else {
        value = 0
      }
      return { framework: fw, value }
    })

    const x = d3.scaleBand().domain(data.map(d => d.framework)).range([0, width - margin.left - margin.right]).padding(0.2)
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value) || 1]).nice().range([height - margin.top - margin.bottom, 0])

    g.append('g').attr('transform', `translate(0,${height - margin.top - margin.bottom})`).call(d3.axisBottom(x))
    g.append('g').call(d3.axisLeft(y))

    const color = (fw: string) => fw === 'utilitarian' ? '#22c55e' : fw === 'fairness' ? '#3b82f6' : '#f59e0b'

    g.selectAll('rect').data(data).enter().append('rect')
      .attr('x', d => x(d.framework)!)
      .attr('y', d => y(d.value))
      .attr('width', x.bandwidth())
      .attr('height', d => (height - margin.top - margin.bottom) - y(d.value))
      .attr('fill', d => color(d.framework))

    g.append('text').attr('x', (width - margin.left - margin.right)/2).attr('y', height - margin.top - 10).attr('text-anchor','middle').text('Framework')
    g.append('text').attr('transform','rotate(-90)').attr('y', -40).attr('x', -(height - margin.top - margin.bottom)/2).attr('text-anchor','middle').text('Score')
  }, [results])

  return <svg ref={ref} className="w-full h-64" />
}