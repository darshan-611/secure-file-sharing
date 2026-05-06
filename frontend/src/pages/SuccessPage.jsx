import { useMemo, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import Alert from "../components/Alert";

export default function SuccessPage() {
  const location = useLocation();
  const [message, setMessage] = useState("");
  const data = location.state;
  const canRender = useMemo(() => Boolean(data?.link), [data]);

  const copy = async () => {
    if (!data?.link) return;
    await navigator.clipboard.writeText(data.link);
    setMessage("Link copied to clipboard.");
  };

  if (!canRender) {
    return (
      <main className="page">
        <section className="card">
          <h1>No upload data</h1>
          <p className="muted">Upload a file first to generate a secure link.</p>
          <Link className="btn" to="/">
            Back to upload
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="page">
      <section className="card">
        <h1>Link Ready</h1>
        <p className="muted">Share this link securely with the recipient.</p>
        <div className="result-box">{data.link}</div>
        <button className="btn" onClick={copy}>
          Copy link
        </button>
        <ul className="details-list">
          <li>File: {data.filename}</li>
          <li>Password protected: {data.requires_password ? "Yes" : "No"}</li>
          <li>One-time link: {data.one_time_download ? "Yes" : "No"}</li>
          <li>Expires at: {new Date(data.expires_at).toLocaleString()}</li>
        </ul>
        <Alert type="success" message={message} />
        <Link className="btn secondary" to="/">
          Upload another file
        </Link>
      </section>
    </main>
  );
}
