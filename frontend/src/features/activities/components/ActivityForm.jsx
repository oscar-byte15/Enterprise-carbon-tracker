
import { useState } from "react";

const activityTypes = {
  electricity: ["Grid electricity"],
  heating: ["Natural gas"],
  transport: ["Petrol", "Diesel"],
  waste: ["Plastic", "Organic", "General"],
};

const units = {
  electricity: "kWh",
  heating: "m³",
  transport: "L",
  waste: "kg",
};

export default function ActivityForm({ onSubmit }) {
  const [category, setCategory] = useState("electricity");
  const [type, setType] = useState("Grid electricity");
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState("");

  function handleCategoryChange(event) {
    const selectedCategory = event.target.value;
    setCategory(selectedCategory);
    setType(activityTypes[selectedCategory][0]);
  }

  function handleSubmit(event) {
    event.preventDefault();

    const activity = {
      category,
      type,
      amount: Number(amount),
      unit: units[category],
      date,
      period: date.slice(0, 7),
    };

    if (onSubmit) {
      onSubmit(activity);
    } else {
      console.log("Activity:", activity);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>New Carbon Activity</h2>

      <div>
        <label htmlFor="category">Category</label>
        <select
          id="category"
          value={category}
          onChange={handleCategoryChange}
        >
          {Object.keys(activityTypes).map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="type">Activity Type</label>
        <select
          id="type"
          value={type}
          onChange={(event) => setType(event.target.value)}
        >
          {activityTypes[category].map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="amount">
          Amount ({units[category]})
        </label>
        <input
          id="amount"
          type="number"
          min="0"
          step="any"
          required
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
        />
      </div>

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

      <button type="submit">Save Activity</button>
    </form>
  );
}
