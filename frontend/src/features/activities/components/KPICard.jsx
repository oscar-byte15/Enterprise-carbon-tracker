export default function KPICard({ title, value, subtitle, badge, icon }) {
  return (
    <div className="kpi-card">
      <div className="kpi-card-header">
        <span className="kpi-title">{title}</span>
        {badge && <span className="kpi-badge">{badge}</span>}
        {icon && <span className="kpi-icon" aria-hidden="true">{icon}</span>}
      </div>

      <div className="kpi-value">{value}</div>

      {subtitle && <div className="kpi-subtitle">{subtitle}</div>}
    </div>
  );
}
