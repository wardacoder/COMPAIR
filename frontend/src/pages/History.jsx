import { useEffect, useState } from "react";
import API_BASE from "../config/api";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await fetch(`${API_BASE}/history/guest123`);
        const data = await res.json();
        setHistory(data.history || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <h1 className="text-3xl font-bold mb-6 text-center text-blue-700">Saved Comparisons</h1>
      {loading && <p className="text-center">Loading...</p>}
      {!loading && history.length === 0 && (
        <p className="text-center text-gray-600">No saved comparisons yet.</p>
      )}
      <div className="space-y-6">
        {history.map((item, i) => (
          <div key={i} className="bg-white shadow-md p-5 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-500 mb-1">
              {new Date(item.timestamp).toLocaleString()}
            </p>
            <h2 className="font-semibold capitalize text-lg">{item.category}</h2>
            <p className="text-gray-700 mt-1">Items: {item.items.join(", ")}</p>
            <p className="mt-2 text-gray-600">
              {item.result?.recommendation || "No recommendation available."}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
