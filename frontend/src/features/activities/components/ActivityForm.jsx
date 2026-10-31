
import { useState } from "react";
import { createActivity } from "../services/activityService";

// Available activity types by category

const activityTypes = {
  electricity: ["Grid electricity"],
  heating: ["Natural gas"],
  transport: ["Petrol", "Diesel"],
  waste: [
    "Plastic - Recycling",
    "Organic - Composting",
    "General - Landfill",
  ],
};

const units = {
  electricity: "kWh",
  heating: "kWh",
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

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Update category and reset activity type
  function handleCategoryChange(event) {
    const selectedCategory = event.target.value;

    setCategory(selectedCategory);
    setType(activityTypes[selectedCategory][0]);
    setError("");
  }

  // Handle CREATE and UPDATE operations
  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    // Validate amount and date
    if (
      !date ||
      amount === "" ||
      !Number.isFinite(Number(amount)) ||
      Number(amount) <= 0
    ) {
      setError("Please enter a valid amount and date.");
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

    setLoading(true);

    try {
      if (mode === "edit") {
        // UPDATE is handled by EditActivity.jsx
        if (!onSubmit) {
          throw new Error("Update handler is missing");
        }

        await onSubmit(activity);
      } else {
        // CREATE using FastAPI
        const savedActivity = await createActivity(activity);

        // Notify parent component
        await onSubmit?.(savedActivity);

        // Clear input fields
        setAmount("");
        setDate("");
      }

      alert(
        mode === "edit"
          ? "Activity updated successfully!"
          : "Activity saved successfully!"
      );
    } catch (err) {
      setError(
        err.message || "Unable to process carbon activity."
      );
    } finally {
      setLoading(false);
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
          disabled={loading}
          required
        >
          {Object.keys(activityTypes).map((item) => (
            <option key={item} value={item}>
              {item.charAt(0).toUpperCase() +
                item.slice(1)}
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
          disabled={loading}
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
          disabled={loading}
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
          disabled={loading}
        />
      </div>

      {/* Error message */}
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}

      {/* Submit */}
      <button type="submit" disabled={loading}>
        {loading
          ? "Processing..."
          : mode === "edit"
            ? "Save Changes"
            : "Save Activity"}
      </button>
    </form>
  );
}
