
import ActivityForm from "../components/ActivityForm";

export default function NewActivity() {
  function handleCreateActivity(activity) {
    console.log("New activity submitted:", activity);
  }

  return (
    <main>
      <h1>Carbon Activity Management</h1>
      <p>Register and manage enterprise carbon activities.</p>

      <ActivityForm onSubmit={handleCreateActivity} />
    </main>
  );
}
