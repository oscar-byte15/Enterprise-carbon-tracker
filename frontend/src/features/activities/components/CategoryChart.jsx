const CATEGORY_COLORS = {
  electricity: "#0e7a6d",
  heating: "#d97706",
  transport: "#2563eb",
  waste: "#7c3aed",
};

const DEFAULT_COLOR = "#64748b";

export default function CategoryChart({ breakdown = [], totalCo2e = 0 }) {
  if (!breakdown || breakdown.length === 0) {
    return (
      <div className="chart-empty-state">
        <p>No category breakdown data available.</p>
      </div>
    );
  }

  // Calculate SVG donut segments
  const radius = 54;
  const circumference = 2 * Math.PI * radius; // ~339.29
  let accumulatedPercent = 0;

  const slices = breakdown.map((item) => {
    const strokeDasharray = `${(item.percentage / 100) * circumference} ${circumference}`;
    const strokeDashoffset = -((accumulatedPercent / 100) * circumference);
    accumulatedPercent += item.percentage;
    const color = CATEGORY_COLORS[item.category.toLowerCase()] || DEFAULT_COLOR;

    return {
      ...item,
      color,
      strokeDasharray,
      strokeDashoffset,
    };
  });

  return (
    <div className="category-chart-container">
      <div className="donut-wrapper">
        <svg
          viewBox="0 0 160 160"
          className="donut-svg"
          aria-label="Category emissions distribution donut chart"
          role="img"
        >
          {/* Background circle track */}
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="transparent"
            stroke="var(--bg-2)"
            strokeWidth="18"
          />

          {/* Slices */}
          {slices.map((slice) => (
            <circle
              key={slice.category}
              cx="80"
              cy="80"
              r={radius}
              fill="transparent"
              stroke={slice.color}
              strokeWidth="18"
              strokeDasharray={slice.strokeDasharray}
              strokeDashoffset={slice.strokeDashoffset}
              transform="rotate(-90 80 80)"
              className="donut-slice"
            >
              <title>{`${slice.category}: ${slice.co2e_kg.toLocaleString()} kg (${slice.percentage}%)`}</title>
            </circle>
          ))}

          {/* Center text */}
          <g className="donut-center-text">
            <text
              x="80"
              y="74"
              textAnchor="middle"
              className="donut-center-value"
            >
              {totalCo2e > 9999
                ? `${(totalCo2e / 1000).toFixed(1)}t`
                : `${Math.round(totalCo2e)}kg`}
            </text>
            <text
              x="80"
              y="92"
              textAnchor="middle"
              className="donut-center-label"
            >
              Total CO2e
            </text>
          </g>
        </svg>
      </div>

      <div className="donut-legend">
        <ul className="donut-legend-list">
          {slices.map((item) => (
            <li key={item.category} className="donut-legend-item">
              <div className="legend-label-group">
                <span
                  className="legend-dot"
                  style={{ backgroundColor: item.color }}
                  aria-hidden="true"
                />
                <span className="legend-category">
                  {item.category.charAt(0).toUpperCase() + item.category.slice(1)}
                </span>
              </div>

              <div className="legend-metrics">
                <span className="legend-co2">
                  {item.co2e_kg.toLocaleString(undefined, {
                    minimumFractionDigits: 1,
                    maximumFractionDigits: 2,
                  })}{" "}
                  kg
                </span>
                <span
                  className="legend-percent-badge"
                  style={{ borderColor: item.color, color: item.color }}
                >
                  {item.percentage}%
                </span>
                <span className="legend-count">
                  {item.activity_count} {item.activity_count === 1 ? "act" : "acts"}
                </span>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
