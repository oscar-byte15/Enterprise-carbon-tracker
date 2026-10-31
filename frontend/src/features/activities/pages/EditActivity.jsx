
import ActivityForm from "../components/ActivityForm";
import { updateActivity } from "../services/activityService";

export default function EditActivity({ activity, onSaved }) {
  // Show message when no activity is selected
  if (!activity) {
    return (
      <div>
        <h2>Edit Activity</h2>
        <p>
          No activity selected. Please go to Activity History
          and click Edit on the activity you want to modify.
        </p>
      </div>
    );
  }

  // UPDATE activity using FastAPI
  async function handleUpdate(updatedData) {
    await updateActivity(activity.id, updatedData);

    // Navigate back to Activity History
    onSaved?.();
  }

  return (
    <div className="edit-activity">
      <p>
        Update the information for this carbon activity.
      </p>

      <ActivityForm
        key={activity.id}
        mode="edit"
        initialData={activity}
        onSubmit={handleUpdate}
      />
    </div>
  );
}
