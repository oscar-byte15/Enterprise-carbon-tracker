import { useMemo, useState } from "react";
import ActivitiesSidebar from "./components/ActivitiesSidebar";
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
  const [activePage, setActivePage] = useState("login");
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
    setActivePage("enterprise");
  }

  function handleLogout() {
    clearAuthSession();
    setIsAuthenticated(false);
    setActivePage("login");
  }

  const pages = useMemo(() => ({
    login: {
      title: "Login",
      component: <Login onAuthenticated={handleAuthenticated} onNavigate={handleNavigate} />,
    },
    register: {
      title: "Register",
      component: <Register onAuthenticated={handleAuthenticated} onNavigate={handleNavigate} />,
    },
    enterprise: {
      title: "Enterprise profile",
      component: <EnterpriseProfile onNavigate={handleNavigate} />,
    },
    departments: {
      title: "Departments",
      component: <Departments onNavigate={handleNavigate} />,
    },
    new: {
      title: "New carbon activity",
      component: <NewActivity />,
    },
    history: {
      title: "Activity history",
      component: <ActivityHistory onEdit={handleEdit} />,
    },
    edit: {
      title: "Edit activity",
      component: <EditActivity activity={selectedActivity} onSaved={handleSaved} />,
    },
  }), [selectedActivity]);

  const currentPage = pages[activePage] || pages.login;

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
              Subsystem 1 · Authentication & Enterprise Management
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
