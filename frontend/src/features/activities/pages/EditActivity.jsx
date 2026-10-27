
import ActivityForm from "../components/ActivityForm";
import { updateActivity } from "../services/activityStorage";

export default function EditActivity({ activity, onSaved }) {

  // Show message when no activity has been selected
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

  // Update existing activity
  function handleUpdate(updatedData) {
    try {
      updateActivity(activity.id, updatedData);

      alert("Activity updated successfully!");

      // Return to Activity History
      if (onSaved) {
        onSaved();
      }

    } catch (error) {
      alert(`Unable to update activity: ${error.message}`);
    }
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
