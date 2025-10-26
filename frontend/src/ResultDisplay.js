export default function ResultDisplay({ result }) {
  if (!result) return null;

  const { introduction, table, pros, cons, recommendation } = result;

  return (
    <div className="w-full max-w-5xl mt-10 text-left bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Result</h2>

      {/* Introduction */}
      {introduction && (
        <p className="mb-6 text-gray-700 leading-relaxed">{introduction}</p>
      )}

      {/* Table */}
      {table && Array.isArray(table) && table.length > 0 && (
        <div className="overflow-x-auto mb-8">
          <table className="min-w-full border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                {Object.keys(table[0]).map((key) => (
                  <th
                    key={key}
                    className="border px-4 py-2 text-left text-sm font-semibold text-gray-700 capitalize"
                  >
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.map((row, i) => (
                <tr key={i} className="border-t hover:bg-gray-50">
                  {Object.values(row).map((value, j) => (
                    <td key={j} className="border px-4 py-2 text-sm text-gray-700">
                      {value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pros and Cons */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {pros && Array.isArray(pros) && pros.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold mb-2 text-green-700">Pros</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              {pros.map((p, idx) => (
                <li key={idx}>{p}</li>
              ))}
            </ul>
          </div>
        )}
        {cons && Array.isArray(cons) && cons.length > 0 && (
          <div>
            <h3 className="text-xl font-semibold mb-2 text-red-700">Cons</h3>
            <ul className="list-disc list-inside text-gray-700 space-y-1">
              {cons.map((c, idx) => (
                <li key={idx}>{c}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Recommendation */}
      {recommendation && (
        <div className="border-t pt-4">
          <h3 className="text-xl font-semibold mb-2 text-blue-700">
            Recommendation
          </h3>
          <p className="text-gray-700">{recommendation}</p>
        </div>
      )}
    </div>
  );
}
