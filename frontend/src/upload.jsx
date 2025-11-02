import React, { useState, useEffect } from "react";
import "./upload.css";

export default function UploadPage() {
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState("");

  useEffect(() => {
    // Fetch available folders from backend
    setFolders(["Folder1", "Folder2"]); // placeholder
  }, []);

  const handleSummarize = () => {
    if (!selectedFolder) return alert("Select a folder!");
    alert(`Summarizing folder: ${selectedFolder}`);
    // Backend will generate summary/video
  };

  return (
    <div className="page-content">
      <h1>Summarize Folder</h1>
      <select
        value={selectedFolder}
        onChange={(e) => setSelectedFolder(e.target.value)}
      >
        <option value="">Select a folder</option>
        {folders.map((f) => (
          <option key={f} value={f}>{f}</option>
        ))}
      </select>
      <button onClick={handleSummarize}>Create Summary</button>
    </div>
  );
}
