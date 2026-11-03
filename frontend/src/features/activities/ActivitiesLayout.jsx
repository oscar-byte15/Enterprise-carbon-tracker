import { useMemo, useState } from "react";
import ActivitiesSidebar from "./components/ActivitiesSidebar";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import AICoach from "./pages/AICoach";
import NewActivity from "./pages/NewActivity";
import ActivityHistory from "./pages/ActivityHistory";
import EditActivity from "./pages/EditActivity";
import Login from "./pages/Login";
import Register from "./pages/Register";
import EnterpriseProfile from "./pages/EnterpriseProfile";
import Departments from "./pages/Departments";
import { clearAuthSession } from "./services/authService";
import "./activities.css";

export default function ActivitiesLayout() {
  const [activePage, setActivePage] = useState("dashboard");
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(localStorage.getItem("enterprise_token")));

  function handleEdit(activity) {
    setSelectedActivity(activity);
    setActivePage("edit");
  }

  function handleNavigate(page) {
    if (page === "edit") {
      setSelectedActivity(null);
    }

    setActivePage(page);
  }

  function handleSaved() {
    setSelectedActivity(null);
    setActivePage("history");
  }

  function handleAuthenticated(result) {
    setIsAuthenticated(Boolean(result?.access_token));
    setActivePage("dashboard");
  }

  function handleLogout() {
    clearAuthSession();
    setIsAuthenticated(false);
    setActivePage("login");
  }

  const pages = useMemo(() => ({
    dashboard: {
      title: "Executive Dashboard",
      subtitle: "Subsystem 3 · Analytics Dashboard & Performance Tracking",
      component: <Dashboard onNavigate={handleNavigate} />,
    },
    analytics: {
      title: "Emissions Analytics & Trends",
      subtitle: "Subsystem 3 · Visual Trend Analysis & Category Distribution",
      component: <Analytics onNavigate={handleNavigate} />,
    },
    "ai-coach": {
      title: "AI Sustainability Advisor",
      subtitle: "Subsystem 3 · Contextual Decarbonization Intelligence",
      component: <AICoach onNavigate={handleNavigate} />,
    },
    login: {
      title: "Login",
      subtitle: "Subsystem 1 · Authentication & Enterprise Management",
      component: <Login onAuthenticated={handleAuthenticated} onNavigate={handleNavigate} />,
    },
    register: {
      title: "Register",
      subtitle: "Subsystem 1 · Authentication & Enterprise Management",
      component: <Register onAuthenticated={handleAuthenticated} onNavigate={handleNavigate} />,
    },
    enterprise: {
      title: "Enterprise profile",
      subtitle: "Subsystem 1 · Authentication & Enterprise Management",
      component: <EnterpriseProfile onNavigate={handleNavigate} />,
    },
    departments: {
      title: "Departments",
      subtitle: "Subsystem 1 · Authentication & Enterprise Management",
      component: <Departments onNavigate={handleNavigate} />,
    },
    new: {
      title: "New carbon activity",
      subtitle: "Subsystem 2 · Carbon Activity Management",
      component: <NewActivity />,
    },
    history: {
      title: "Activity history",
      subtitle: "Subsystem 2 · Carbon Activity Management",
      component: <ActivityHistory onEdit={handleEdit} />,
    },
    edit: {
      title: "Edit activity",
      subtitle: "Subsystem 2 · Carbon Activity Management",
      component: <EditActivity activity={selectedActivity} onSaved={handleSaved} />,
    },
  }), [selectedActivity]);

  const currentPage = pages[activePage] || pages.dashboard;

  return (
    <div className="activities-layout">
      <ActivitiesSidebar
        activePage={activePage}
        onNavigate={handleNavigate}
        isAuthenticated={isAuthenticated}
        onLogout={handleLogout}
      />

      <main className="activities-main">
        <header className="activities-header">
          <div>
            <h1>{currentPage.title}</h1>
            <p>
              {currentPage.subtitle}
            </p>
          </div>

          <div className="activities-header-actions">
            {isAuthenticated ? (
              <button type="button" className="logout-button" onClick={handleLogout}>Log out</button>
            ) : null}
            <span className="activities-status">{isAuthenticated ? "SIGNED IN" : "AUTH REQUIRED"}</span>
          </div>
        </header>

        <section className="activities-content">
          {currentPage.component}
        </section>
      </main>
    </div>
  );
}
