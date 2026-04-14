function LoadingBlock({ title = "Loading data..." }) {
  return (
    <div className="card loading-card">
      <div className="loader" />
      <p>{title}</p>
    </div>
  );
}

export default LoadingBlock;
