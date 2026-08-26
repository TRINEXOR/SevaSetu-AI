/** SevaSetu AI — LoadingSpinner | Rahul Jha */
export default function LoadingSpinner({ fullscreen, size = "md" }) {
  if (fullscreen) return (
    <div className="loading-fullscreen">
      <div className={`spinner ${size}`} />
      <div style={{ fontSize:"0.85rem", color:"var(--text-2)", marginTop:8 }}>Loading SevaSetu AI...</div>
      <div style={{ fontSize:"0.72rem", color:"var(--text-3)", marginTop:4 }}>Made in India 🇮🇳 by Rahul Jha</div>
    </div>
  );
  return <div className={`spinner ${size}`} />;
}
