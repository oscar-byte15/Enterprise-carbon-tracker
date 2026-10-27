
const STORAGE_KEY = "carbontrack_activities";

export function getActivities() {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(stored) ? stored : [];
  } catch {
    return [];
  }
}

export function saveActivity(activity) {
  const activities = getActivities();

  const newActivity = {
    ...activity,
    id: crypto.randomUUID(),
    createdAt: new Date().toISOString(),
  };

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify([...activities, newActivity])
  );

  return newActivity;
}

export function deleteActivity(id) {
  const activities = getActivities();
  const updated = activities.filter((activity) => activity.id !== id);

  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}


export function updateActivity(id, updatedData) {
  const activities = getActivities();

  const existingActivity = activities.find(
    (activity) => activity.id === id
  );

  if (!existingActivity) {
    throw new Error("Activity not found");
  }

  const updatedActivities = activities.map((activity) =>
    activity.id === id
      ? {
          ...activity,
          ...updatedData,
          id: activity.id,
          createdAt: activity.createdAt,
          updatedAt: new Date().toISOString(),
        }
      : activity
  );

  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify(updatedActivities)
  );

  return updatedActivities.find(
    (activity) => activity.id === id
  );
}
