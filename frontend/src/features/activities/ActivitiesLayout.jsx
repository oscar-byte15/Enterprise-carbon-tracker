
import { useState } from "react";
import ActivitiesSidebar from "./components/ActivitiesSidebar";
import NewActivity from "./pages/NewActivity";
import ActivityHistory from "./pages/ActivityHistory";
import EditActivity from "./pages/EditActivity";
import "./activities.css";

export default function ActivitiesLayout() {
  const [activePage, setActivePage] = useState("new");

  const pages = {
    new: {
      title: "New carbon activity",
      component: <NewActivity />,
    },
    history: {
      title: "Activity history",
      component: <ActivityHistory />,
    },
    edit: {
      title: "Edit activity",
      component: <EditActivity />,
    },
  };

  const currentPage = pages[activePage];

  return (
    <div className="activities-layout">
      <ActivitiesSidebar
        activePage={activePage}
        onNavigate={setActivePage}
      />

      <main className="activities-main">
        <header className="activities-header">
          <div>
            <h1>{currentPage.title}</h1>
            <p>Subsystem 2 · Carbon Activity Management</p>
          </div>
          <span className="activities-status">DEVELOPMENT</span>
        </header>

        <section className="activities-content">
          {currentPage.component}
        </section>
      </main>
    </div>
  );
}
