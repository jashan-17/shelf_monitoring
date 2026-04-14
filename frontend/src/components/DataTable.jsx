function DataTable({ rows }) {
  if (!rows.length) {
    return (
      <div className="card empty-state">
        <h3>No predictions yet</h3>
        <p className="card-copy">
          As soon as new predictions are written to PostgreSQL, they will appear
          here.
        </p>
      </div>
    );
  }

  return (
    <div className="card table-card">
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Image</th>
              <th>Actual</th>
              <th>Predicted</th>
              <th>Confidence</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.image_name}</td>
                <td>{row.actual_label || "N/A"}</td>
                <td>
                  <span className={`tag tag-${row.predicted_label}`}>
                    {row.predicted_label}
                  </span>
                </td>
                <td>{(row.confidence * 100).toFixed(1)}%</td>
                <td>{new Date(row.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default DataTable;
