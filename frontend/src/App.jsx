import { Navigate, Route, Routes } from "react-router-dom";

import UploadPage from "./pages/UploadPage";
import SuccessPage from "./pages/SuccessPage";
import DownloadPage from "./pages/DownloadPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<UploadPage />} />
      <Route path="/success" element={<SuccessPage />} />
      <Route path="/download/:token" element={<DownloadPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}