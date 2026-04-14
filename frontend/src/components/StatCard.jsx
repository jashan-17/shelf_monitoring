function StatCard({ label, value, accent, hint }) {
  return (
    <div className="card stat-card">
      <div className={`stat-accent stat-accent-${accent || "default"}`} />
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      {hint ? <p className="card-copy">{hint}</p> : null}
    </div>
  );
}

export default StatCard;
