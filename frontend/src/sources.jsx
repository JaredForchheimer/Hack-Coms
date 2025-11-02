import React, { useState } from "react";

export default function SourcesPage() {
  const [files, setFiles] = useState([]);
  const [folderName, setFolderName] = useState("");

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = () => {
    if (!folderName) return alert("Enter folder name!");
    if (!files.length) return alert("Select files to upload!");

    // Call backend API safely
    // Example: POST /api/sources/upload
    alert(`Uploading ${files.length} file(s) to folder "${folderName}"`);
  };

  return (
    <div style={{ padding: "1rem", color: "#e5e5e5" }}>
      <h1>Upload Sources</h1>
      <input
        type="text"
        placeholder="Folder name"
        value={folderName}
        onChange={(e) => setFolderName(e.target.value)}
        style={{ marginBottom: "1rem", padding: "0.5rem" }}
      />
      <input type="file" multiple onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ display: "block", marginTop: "1rem", padding: "0.5rem 1rem", backgroundColor:"#ff7e5f", color:"#fff", border:"none", borderRadius:"8px" }}>Upload</button>
    </div>
  );
}
