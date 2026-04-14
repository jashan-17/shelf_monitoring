function ErrorBlock({ message, onRetry }) {
  return (
    <div className="card error-card">
      <h3>Unable to load data</h3>
      <p className="card-copy">{message}</p>
      {onRetry ? (
        <button className="button button-secondary" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}

export default ErrorBlock;
