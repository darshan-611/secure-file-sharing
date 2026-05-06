import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Alert from "../components/Alert";
import FileDropzone from "../components/FileDropzone";
import ProgressBar from "../components/ProgressBar";
import { uploadFile } from "../services/api";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [password, setPassword] = useState("");
  const [expiryHours, setExpiryHours] = useState(24);
  const [oneTimeDownload, setOneTimeDownload] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (event) => {
    event.preventDefault();
    setError("");
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    if (password.trim()) formData.append("password", password.trim());
    formData.append("expiry_hours", String(expiryHours));
    formData.append("one_time_download", String(oneTimeDownload));

    setSubmitting(true);
    try {
      const data = await uploadFile(formData, (eventProgress) => {
        const total = eventProgress.total || file.size || 1;
        const percent = (eventProgress.loaded / total) * 100;
        setProgress(percent);
      });
      navigate("/success", { state: data });
    } catch (err) {
      const detail = err?.response?.data?.detail || "Upload failed. Please try again.";
      setError(detail);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page">
      <section className="card">
        <h1>Secure File Sharing</h1>
        <p className="muted">Files are encrypted with AES-GCM before storage.</p>
        <form onSubmit={onSubmit} className="form">
          <FileDropzone file={file} onFileChange={setFile} />
          <label>
            Password (optional)
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Protect this link with a password"
            />
          </label>
          <label>
            Expiry in hours
            <input
              type="number"
              min={1}
              max={168}
              value={expiryHours}
              onChange={(event) => setExpiryHours(Number(event.target.value))}
            />
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={oneTimeDownload}
              onChange={(event) => setOneTimeDownload(event.target.checked)}
            />
            One-time download only
          </label>
          {submitting && <ProgressBar value={progress} />}
          <button className="btn" disabled={submitting}>
            {submitting ? "Uploading..." : "Upload Securely"}
          </button>
          <Alert type="error" message={error} />
        </form>
      </section>
    </main>
  );
}
