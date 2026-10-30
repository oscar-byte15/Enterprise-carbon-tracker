const menuItems = [
  { id: "login", label: "Login" },
  { id: "register", label: "Register & onboarding" },
  { id: "enterprise", label: "Enterprise profile" },
  { id: "departments", label: "Departments" },
  { id: "new", label: "New carbon activity" },
  { id: "history", label: "Activity history" },
  { id: "edit", label: "Edit activity" },
];

export default function ActivitiesSidebar({
  activePage,
  onNavigate,
  isAuthenticated,
  onLogout,
}) {
  return (
    <aside className="activities-sidebar">
      <div className="activities-brand">
        <h2>◉ CarbonTrack</h2>
        <p>Enterprise platform</p>
      </div>

      <nav className="activities-nav" aria-label="CarbonTrack navigation">
        {menuItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`activities-nav-item ${
              activePage === item.id ? "active" : ""
            }`}
            onClick={() => onNavigate(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {isAuthenticated ? (
        <button type="button" className="sidebar-logout" onClick={onLogout}>
          Log out
        </button>
      ) : null}

      <div className="activities-sidebar-footer">
        Subsystem 1 · Authentication & Enterprise
        <small>Local demo mode</small>
      </div>
    </aside>
  );
}
