export default function ProgressBar({ value }) {
  const width = Math.max(0, Math.min(100, Number(value) || 0));
  return (
    <div className="progress-wrap">
      <div className="progress-bar" style={{ width: `${width}%` }} />
      <span className="progress-label">{Math.round(width)}%</span>
    </div>
  );
}
