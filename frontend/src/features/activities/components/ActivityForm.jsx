
import { useState } from "react";
import { saveActivity } from "../services/activityStorage";

// Available activity types by category
const activityTypes = {
  electricity: ["Grid electricity"],
  heating: ["Natural gas"],
  transport: ["Petrol", "Diesel"],
  waste: ["Plastic", "Organic", "General"],
};

// Measurement units by category
const units = {
  electricity: "kWh",
  heating: "m³",
  transport: "L",
  waste: "kg",
};

export default function ActivityForm({
  onSubmit,
  initialData = null,
  mode = "create",
}) {
  // Form state
  const [category, setCategory] = useState(
    initialData?.category || "electricity"
  );

  const [type, setType] = useState(
    initialData?.type || "Grid electricity"
  );

  const [amount, setAmount] = useState(
    initialData?.amount ?? ""
  );

  const [date, setDate] = useState(
    initialData?.date || ""
  );

  // Update category and reset activity type
  function handleCategoryChange(event) {
    const selectedCategory = event.target.value;

    setCategory(selectedCategory);
    setType(activityTypes[selectedCategory][0]);
  }

  // Handle Create and Update operations
  function handleSubmit(event) {
    event.preventDefault();

    // Validate amount and date
    if (
      !date ||
      amount === "" ||
      !Number.isFinite(Number(amount)) ||
      Number(amount) <= 0
    ) {
      alert("Please enter a valid amount and date.");
      return;
    }

    // Prepare activity data
    const activity = {
      category,
      type,
      amount: Number(amount),
      unit: units[category],
      date,
      period: date.slice(0, 7),
    };

    if (mode === "edit") {
      // Edit mode: parent updates the existing activity
      if (onSubmit) {
        onSubmit(activity);
      }
    } else {
      // Create mode: save a new activity
      try {
        const savedActivity = saveActivity(activity);

        // Notify parent if callback exists
        if (onSubmit) {
          onSubmit(savedActivity);
        }

        alert("Activity saved successfully!");

        // Clear input fields after saving
        setAmount("");
        setDate("");
      } catch (error) {
        alert(`Unable to save activity: ${error.message}`);
      }
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>
        {mode === "edit"
          ? "Edit Carbon Activity"
          : "New Carbon Activity"}
      </h2>

      {/* Category */}
      <div>
        <label htmlFor="category">Category</label>

        <select
          id="category"
          value={category}
          onChange={handleCategoryChange}
          required
        >
          {Object.keys(activityTypes).map((item) => (
            <option key={item} value={item}>
              {item.charAt(0).toUpperCase() + item.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Activity Type */}
      <div>
        <label htmlFor="type">Activity Type</label>

        <select
          id="type"
          value={type}
          onChange={(event) => setType(event.target.value)}
          required
        >
          {activityTypes[category].map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      {/* Amount */}
      <div>
        <label htmlFor="amount">
          Amount ({units[category]})
        </label>

        <input
          id="amount"
          type="number"
          min="0.01"
          step="any"
          required
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          placeholder={`Enter amount in ${units[category]}`}
        />
      </div>

      {/* Date */}
      <div>
        <label htmlFor="date">Date</label>

        <input
          id="date"
          type="date"
          required
          value={date}
          onChange={(event) => setDate(event.target.value)}
        />
      </div>

      {/* Submit button */}
      <button type="submit">
        {mode === "edit" ? "Save Changes" : "Save Activity"}
      </button>
    </form>
  );
}
