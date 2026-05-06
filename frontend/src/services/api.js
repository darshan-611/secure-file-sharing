import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL:'http://localhost:8000/api',
});

export async function uploadFile(formData, onUploadProgress) {
  const { data } = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return data;
}

export async function fetchFileStatus(token) {
  const { data } = await api.get(`/files/${token}`);
  return data;
}

export async function verifyPassword(token, password) {
  const payload = new FormData();
  payload.append("token", token);
  payload.append("password", password);
  const { data } = await api.post("/verify-password", payload);
  return data;
}

export function buildDownloadUrl(token, grant) {
  const grantParam = grant ? `?grant=${encodeURIComponent(grant)}` : "";
  return `${API_BASE_URL}/download/${token}${grantParam}`;
}
