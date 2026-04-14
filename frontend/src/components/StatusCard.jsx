function StatusCard({ label, status, detail }) {
  return (
    <div className="card status-card">
      <div className="status-row">
        <span>{label}</span>
        <span className={`status-pill status-${status}`}>{status}</span>
      </div>
      <p className="card-copy">{detail}</p>
    </div>
  );
}

export default StatusCard;
