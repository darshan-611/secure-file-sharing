import axios from "axios";

// Production backend URL from Vercel environment variable
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "https://secure-file-sharing-api-px58.onrender.com";

// Axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

// Upload file
export async function uploadFile(formData, onUploadProgress) {
  const { data } = await api.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress,
  });

  return data;
}

// Fetch file status
export async function fetchFileStatus(token) {
  const { data } = await api.get(`/files/${token}`);
  return data;
}

// Verify password
export async function verifyPassword(token, password) {
  const payload = new FormData();

  payload.append("token", token);
  payload.append("password", password);

  const { data } = await api.post("/verify-password", payload);

  return data;
}

// Build download URL
export function buildDownloadUrl(token, grant) {
  const grantParam = grant
    ? `?grant=${encodeURIComponent(grant)}`
    : "";

  return `${API_BASE_URL}/api/download/${token}${grantParam}`;
}
