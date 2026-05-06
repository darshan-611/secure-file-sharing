import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Alert from "../components/Alert";
import { buildDownloadUrl, fetchFileStatus, verifyPassword } from "../services/api";

export default function DownloadPage() {
  const { token } = useParams();
  const [status, setStatus] = useState(null);
  const [password, setPassword] = useState("");
  const [grant, setGrant] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        const data = await fetchFileStatus(token);
        setStatus(data);
      } catch (err) {
        setError(err?.response?.data?.detail || "Could not load file details.");
      }
    };
    run();
  }, [token]);

  const verify = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const data = await verifyPassword(token, password);
      setGrant(data.grant);
      setMessage("Password verified. You can download now.");
    } catch (err) {
      setError(err?.response?.data?.detail || "Password verification failed.");
    }
  };

  if (error && !status) {
    return (
      <main className="page">
        <section className="card">
          <h1>Download unavailable</h1>
          <Alert type="error" message={error} />
          <Link className="btn" to="/">
            Upload new file
          </Link>
        </section>
      </main>
    );
  }

  const blocked = status?.is_expired || (status?.one_time_download && status?.downloaded);
  const requiresPassword = status?.requires_password && !grant;
  const downloadUrl = buildDownloadUrl(token, grant);

  return (
    <main className="page">
      <section className="card">
        <h1>Download Secure File</h1>
        <p className="muted">File: {status?.filename || "Loading..."}</p>
        {blocked ? (
          <Alert type="error" message="This link is expired or already used." />
        ) : (
          <>
            {requiresPassword && (
              <form onSubmit={verify} className="form">
                <label>
                  Enter password
                  <input
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                  />
                </label>
                <button className="btn">Verify Password</button>
              </form>
            )}
            {!requiresPassword && (
              <a className="btn" href={downloadUrl}>
                Download File
              </a>
            )}
          </>
        )}
        <Alert type="success" message={message} />
        <Alert type="error" message={error} />
      </section>
    </main>
  );
}
