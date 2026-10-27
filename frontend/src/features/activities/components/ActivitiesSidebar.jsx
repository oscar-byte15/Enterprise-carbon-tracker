
const menuItems = [
  { id: "login", label: "Login", external: true },
  { id: "register", label: "Register & onboarding", external: true },
  { id: "dashboard", label: "Dashboard", external: true },
  { id: "enterprise", label: "Enterprise profile", external: true },
  { id: "departments", label: "Departments", external: true },
  { id: "history", label: "Activity history" },
  { id: "new", label: "New carbon activity" },
  { id: "edit", label: "Edit activity" },
  { id: "analytics", label: "Analytics & trends", external: true },
  { id: "ai", label: "AI sustainability coach", external: true },
];

export default function ActivitiesSidebar({ activePage, onNavigate }) {
  return (
    <aside className="activities-sidebar">
      <div className="activities-brand">
        <h2>◉ CarbonTrack</h2>
        <p>Carbon Activity Management</p>
      </div>

      <nav className="activities-nav" aria-label="CarbonTrack navigation">
        {menuItems.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={item.external}
            className={`activities-nav-item ${
              activePage === item.id ? "active" : ""
            }`}
            onClick={() => onNavigate(item.id)}
          >
            {item.label}
            {item.external && <span className="activities-pending">Soon</span>}
          </button>
        ))}
      </nav>

      <div className="activities-sidebar-footer">
        Subsystem 2 · Activities & CO₂e
        <small>Independent development preview</small>
      </div>
    </aside>
  );
}
