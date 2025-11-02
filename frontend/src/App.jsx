import React, { useState, useEffect } from "react";
import "./index.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [lang, setLang] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchStorage = async () => {
    const res = await fetch("http://localhost:5000/api/storage");
    const data = await res.json();
    setResults(Object.entries(data));
  };

  useEffect(() => {
    fetchStorage();
  }, []);

  const handleProcess = async () => {
    if (!url) return alert("Please enter a URL.");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, lang }),
      });

      const data = await res.json();

      if (data.error) {
        alert(data.error);
      } else {
        setResults((r) => [...r, [url, data]]);
      }
    } catch (err) {
      alert("Error processing URL: " + err.message);
    } finally {
      setLoading(false);
      setUrl("");
      setLang("");
    }
  };

  return (
    <div className="container">
      <h1>Content Processor</h1>

      <div className="input-group">
        <input
          type="text"
          placeholder="Enter URL..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <input
          type="text"
          placeholder="Translate summary to (optional)... e.g., Spanish or ASL"
          value={lang}
          onChange={(e) => setLang(e.target.value)}
        />
        <button onClick={handleProcess} disabled={loading}>
          {loading ? "Processing..." : "Process URL"}
        </button>
      </div>

      <hr />

      <h2>Stored Summaries</h2>
      {results.length === 0 && <p>No stored content yet.</p>}

      <div className="summaries">
        {results.map(([url, data]) => (
          <div key={url} className="summary-card">
            <p className="url">🔗 {url}</p>
            <p className="summary">{data.summary}</p>

            {/* ASL video - Check both translation_type and translation_lang */}
            {data.translation && 
             (data.translation_type === "ASL" || data.translation_lang === "ASL") && (
              <div className="translation-video">
                <p>🤟 ASL Video:</p>
                <video
                  controls
                  width="400"
                  style={{ marginTop: "10px" }}
                  src={`http://localhost:5000/api/video?path=${encodeURIComponent(
                    data.translation
                  )}`}
                />
              </div>
            )}

            {/* Audio translation for non-ASL languages */}
            {data.translation && 
             data.translation_type !== "ASL" && 
             data.translation_lang !== "ASL" && (
              <div className="translation-audio">
                <p>🌍 {data.translation_lang.charAt(0).toUpperCase() + data.translation_lang.slice(1)} Audio:</p>
                <audio controls>
                  <source
                    src={`http://localhost:5000/api/audio?path=${encodeURIComponent(
                      data.translation
                    )}`}
                    type="audio/mpeg"
                  />
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}