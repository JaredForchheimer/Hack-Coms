import React, { useState, useEffect, useRef } from "react";
import "./sources.css";

export default function Sources() {
  const [folderName, setFolderName] = useState("");
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState("");
  const [currentFolderContents, setCurrentFolderContents] = useState({ urls: [], files: [] });
  const [urlInput, setUrlInput] = useState("");
  const [files, setFiles] = useState(null);
  const fileInputRef = useRef(null);

  // fetch folder list
  const fetchFolders = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/folders");
      const names = await res.json();
      setFolders(Array.isArray(names) ? names.map((n) => ({ name: n })) : []);
    } catch (err) {
      console.error("Error fetching folders:", err);
      setFolders([]);
    }
  };

  useEffect(() => {
    fetchFolders();
  }, []);

  // fetch contents for a folder
  const fetchFolderContents = async (folder) => {
    if (!folder) {
      setCurrentFolderContents({ urls: [], files: [] });
      return;
    }
    try {
      const res = await fetch(
        `http://localhost:5000/api/folder_contents?folder=${encodeURIComponent(folder)}`
      );
      const data = await res.json();
      const urls = (data || []).filter((it) => it.type === "url").map((i) => i.value);
      const filesList = (data || [])
        .filter((it) => it.type === "video")
        .map((i) => (i && i.value ? { name: i.value } : { name: "unknown" }));
      setCurrentFolderContents({ urls, files: filesList });
    } catch (err) {
      console.error("Error fetching folder contents:", err);
      setCurrentFolderContents({ urls: [], files: [] });
    }
  };

  // create folder
  const createFolder = async () => {
    const name = folderName.trim();
    if (!name) return alert("Enter a folder name.");
    try {
      const res = await fetch("http://localhost:5000/api/create_folder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: name }),
      });
      const data = await res.json();
      if (data && data.error) alert(data.error);
      else {
        setFolderName("");
        fetchFolders();
      }
    } catch (err) {
      alert("Error creating folder: " + err.message);
    }
  };

  // add url
  const addURL = async () => {
    const url = urlInput.trim();
    if (!selectedFolder || !url) return alert("Select a folder and enter a URL.");
    try {
      const res = await fetch("http://localhost:5000/api/add_source", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder: selectedFolder, type: "url", value: url }),
      });
      const data = await res.json();
      if (data && data.error) alert(data.error);
      else {
        setUrlInput("");
        fetchFolderContents(selectedFolder);
      }
    } catch (err) {
      alert("Error adding URL: " + err.message);
    }
  };

  // upload files
  const addFiles = async () => {
    if (!selectedFolder || !files) return alert("Select a folder and files.");
    const formData = new FormData();
    formData.append("folder", selectedFolder);
    for (let i = 0; i < files.length; i++) formData.append("files", files[i]);
    try {
      const res = await fetch("http://localhost:5000/api/add_files", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data && data.error) alert(data.error);
      else {
        setFiles(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        fetchFolderContents(selectedFolder);
      }
    } catch (err) {
      alert("Error uploading files: " + err.message);
    }
  };

  const handleSelectFolder = (e) => {
    const name = e.target.value;
    setSelectedFolder(name);
    fetchFolderContents(name);
  };

  return (
    <div className="sources-page">
      <div className="sources-center">
        <div className="sources-container" role="main" aria-label="Sources">
          <section className="action-block">
            <h2>Create Folder</h2>
            <input
              type="text"
              placeholder="Folder Name"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              aria-label="Folder Name"
            />
            <button onClick={createFolder}>Create</button>
          </section>

          <section className="action-block">
            <h2>Add Source to Folder</h2>

            <label className="label-inline" htmlFor="folder-select">Select Folder</label>
            <select id="folder-select" value={selectedFolder} onChange={handleSelectFolder}>
              <option value="">Select a folder...</option>
              {folders.map((f) => (
                <option key={f.name} value={f.name}>
                  {f.name}
                </option>
              ))}
            </select>

            <div className="source-section">
              <h3>Add URL</h3>
              <input
                type="text"
                placeholder="Enter URL"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                aria-label="Enter URL"
              />
              <button onClick={addURL}>Add URL</button>
            </div>

            <div className="source-section">
              <h3>Add Files / Videos</h3>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={(e) => setFiles(e.target.files)}
                aria-label="Choose files"
              />
              <button onClick={addFiles}>Upload Files</button>
            </div>
          </section>

          {selectedFolder && (
            <section className="folder-contents">
              <h2>Contents of {selectedFolder}</h2>

              <div className="folder-section">
                <h3>URLs</h3>
                <ul>
                  {currentFolderContents.urls.length > 0 ? (
                    currentFolderContents.urls.map((url, i) => (
                      <li key={i}><a href={url} target="_blank" rel="noreferrer">{url}</a></li>
                    ))
                  ) : (
                    <li>No URLs added yet</li>
                  )}
                </ul>
              </div>

              <div className="folder-section">
                <h3>Files / Videos</h3>
                <ul>
                  {currentFolderContents.files.length > 0 ? (
                    currentFolderContents.files.map((file, i) => <li key={i}>{file.name}</li>)
                  ) : (
                    <li>No files added yet</li>
                  )}
                </ul>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}