
import { useState } from "react";
import ActivitiesSidebar from "./components/ActivitiesSidebar";
import NewActivity from "./pages/NewActivity";
import ActivityHistory from "./pages/ActivityHistory";
import EditActivity from "./pages/EditActivity";
import "./activities.css";

export default function ActivitiesLayout() {
  // Current page displayed in the sidebar
  const [activePage, setActivePage] = useState("new");

  // Activity selected for editing
  const [selectedActivity, setSelectedActivity] = useState(null);

  // Open Edit Activity with selected record
  function handleEdit(activity) {
    setSelectedActivity(activity);
    setActivePage("edit");
  }

  // Handle navigation from sidebar
  function handleNavigate(page) {
    if (page === "edit") {
      setSelectedActivity(null);
    }

    setActivePage(page);
  }

  // Handle successful update
  function handleSaved() {
    setSelectedActivity(null);
    setActivePage("history");
  }

  const pages = {
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
      component: (
        <EditActivity
          activity={selectedActivity}
          onSaved={handleSaved}
        />
      ),
    },
  };

  const currentPage = pages[activePage];

  return (
    <div className="activities-layout">
      {/* Sidebar */}
      <ActivitiesSidebar
        activePage={activePage}
        onNavigate={handleNavigate}
      />

      {/* Main content */}
      <main className="activities-main">
        <header className="activities-header">
          <div>
            <h1>{currentPage.title}</h1>
            <p>
              Subsystem 2 · Carbon Activity Management
            </p>
          </div>

          <span className="activities-status">
            DEVELOPMENT
          </span>
        </header>

        <section className="activities-content">
          {currentPage.component}
        </section>
      </main>
    </div>
  );
}
