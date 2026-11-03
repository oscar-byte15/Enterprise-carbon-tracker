import { useState } from "react";

export default function TrendChart({ trends = [] }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!trends || trends.length === 0) {
    return (
      <div className="chart-empty-state">
        <p>No monthly emissions trend recorded for this selection.</p>
      </div>
    );
  }

  // Chart configuration
  const svgWidth = 620;
  const svgHeight = 220;
  const margin = { top: 30, right: 20, bottom: 40, left: 55 };
  const plotWidth = svgWidth - margin.left - margin.right;
  const plotHeight = svgHeight - margin.top - margin.bottom;

  // Max value calculation for Y-scale
  const rawMax = Math.max(...trends.map((t) => t.total_co2e_kg), 10);
  const yMax = Math.ceil(rawMax * 1.15); // Add 15% headroom for top labels

  // Grid steps (3 intervals: 0, 50%, 100%)
  const gridSteps = [0, yMax / 2, yMax];

  const barSlotWidth = plotWidth / trends.length;
  const barWidth = Math.min(46, Math.max(16, barSlotWidth * 0.6));

  return (
    <div className="trend-chart-container">
      <svg
        viewBox={`0 0 ${svgWidth} ${svgHeight}`}
        className="trend-svg"
        aria-label="Monthly carbon emissions trend bar chart"
        role="img"
      >
        {/* Horizontal gridlines & Y-axis labels */}
        {gridSteps.map((val, i) => {
          const yPos = margin.top + plotHeight - (val / yMax) * plotHeight;
          return (
            <g key={i} className="chart-grid-row">
              <line
                x1={margin.left}
                y1={yPos}
                x2={margin.left + plotWidth}
                y2={yPos}
                stroke="var(--panel-border)"
                strokeDasharray="4 4"
                strokeWidth="1"
              />
              <text
                x={margin.left - 8}
                y={yPos + 4}
                textAnchor="end"
                className="chart-axis-label"
              >
                {val >= 1000 ? `${(val / 1000).toFixed(1)}t` : `${Math.round(val)}kg`}
              </text>
            </g>
          );
        })}

        {/* Baseline */}
        <line
          x1={margin.left}
          y1={margin.top + plotHeight}
          x2={margin.left + plotWidth}
          y2={margin.top + plotHeight}
          stroke="var(--panel-border)"
          strokeWidth="1.5"
        />

        {/* Bars and labels */}
        {trends.map((item, index) => {
          const barHeight = Math.max((item.total_co2e_kg / yMax) * plotHeight, 3);
          const x = margin.left + index * barSlotWidth + (barSlotWidth - barWidth) / 2;
          const y = margin.top + plotHeight - barHeight;
          const isHovered = hoveredIndex === index;

          return (
            <g
              key={item.period}
              className={`chart-bar-group ${isHovered ? "active" : ""}`}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
              tabIndex="0"
            >
              {/* Value on top of bar */}
              <text
                x={x + barWidth / 2}
                y={y - 8}
                textAnchor="middle"
                className="chart-bar-value"
              >
                {item.total_co2e_kg.toLocaleString(undefined, {
                  maximumFractionDigits: 1,
                })}
              </text>

              {/* Bar rectangle */}
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                rx="6"
                className="chart-bar-rect"
                fill={isHovered ? "var(--brand-strong)" : "var(--brand)"}
              >
                <title>{`${item.period}: ${item.total_co2e_kg.toLocaleString()} kg (${item.activity_count} activities)`}</title>
              </rect>

              {/* Period label under X-axis */}
              <text
                x={x + barWidth / 2}
                y={margin.top + plotHeight + 20}
                textAnchor="middle"
                className="chart-axis-label period-label"
              >
                {item.period}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Summary caption under trend */}
      <div className="trend-footer">
        <span>Unit: kg CO2e</span>
        <span>
          Total Periods: <strong>{trends.length}</strong>
        </span>
      </div>
    </div>
  );
}
