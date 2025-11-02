import React, { useState } from "react";
import "./sources.css";

export default function SourcesPage() {
  const [files, setFiles] = useState([]);
  const [folderName, setFolderName] = useState("");

  const handleFileChange = (e) => setFiles(e.target.files);

  const handleUpload = () => {
    if (!folderName) return alert("Enter folder name!");
    if (!files.length) return alert("Select files to upload!");
    alert(`Uploading ${files.length} file(s) to folder "${folderName}"`);
  };

  return (
    <div className="page-content">
      <h1>Upload Sources</h1>
      <input
        type="text"
        placeholder="Folder name"
        value={folderName}
        onChange={(e) => setFolderName(e.target.value)}
      />
      <input type="file" multiple onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}
