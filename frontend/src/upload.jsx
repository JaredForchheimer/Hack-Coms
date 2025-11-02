import React, { useState, useEffect } from "react";
import "./upload.css";

export default function Upload() {
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Fetch folders from backend
  const fetchFolders = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/folders");
      const data = await res.json();
      setFolders(data);
      if (data.length > 0 && !selectedFolder) setSelectedFolder(data[0]);
    } catch (err) {
      console.error("Error fetching folders:", err);
    }
  };

  useEffect(() => {
    fetchFolders();
  }, []);

  const handleSummarize = async () => {
    if (!selectedFolder) return alert("Please select a folder.");
    setLoading(true);
    setMessage("");

    try {
      const res = await fetch(`http://localhost:5000/api/summarize_folder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: selectedFolder }),
      });

      const data = await res.json();

      if (data.error) {
        alert(data.error);
      } else {
        setMessage(
          "Folder summarized successfully! The summary is now in Home feed."
        );
      }
    } catch (err) {
      alert("Error summarizing folder: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Summarize a Folder of Sources</h2>
      <div className="upload-form">
        <label htmlFor="folder-select">Select Folder:</label>
        <select
          id="folder-select"
          value={selectedFolder}
          onChange={(e) => setSelectedFolder(e.target.value)}
        >
          <option value="">Select a folder...</option>
          {folders.map((folder) => (
            <option key={folder} value={folder}>
              {folder}
            </option>
          ))}
        </select>

        <button onClick={handleSummarize} disabled={loading}>
          {loading ? "Summarizing..." : "Summarize Folder"}
        </button>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
}
