import React, { useState, useEffect } from "react";
import "./index.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [lang, setLang] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch stored summaries
  const fetchStorage = async () => {
    const res = await fetch("http://localhost:5000/api/storage");
    const data = await res.json();
    setResults(Object.entries(data));
  };

  useEffect(() => {
    fetchStorage();
  }, []);
useEffect(() => {
  const page = document.querySelector(".page-content");

  const handleScroll = () => {
    if (page.scrollTop > 50) {
      page.classList.add("scrolled");
    } else {
      page.classList.remove("scrolled");
    }
  };

  page.addEventListener("scroll", handleScroll);

  return () => page.removeEventListener("scroll", handleScroll);
}, []);
  // Handle posting a new URL
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
        setResults((r) => [[url, data], ...r]); // newest posts at top
      }
    } catch (err) {
      alert("Error processing URL: " + err.message);
    } finally {
      setLoading(false);
      setUrl("");
      setLang("");
    }
  };

  // Scroll effect for header
  useEffect(() => {
    const handleScroll = () => {
      const page = document.querySelector(".page-content");
      if (window.scrollY > 50) {
        page.classList.add("scrolled");
      } else {
        page.classList.remove("scrolled");
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []); // <- top level useEffect

  return (
    <div className="page-content">
  <header className="feed-header">ASL News Feed</header>

  <div className="feed-scroll">
    <div className="input-section">
      <input
        type="text"
        placeholder="Enter URL..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <input
        type="text"
        placeholder="Translate summary to (optional)... e.g., ASL"
        value={lang}
        onChange={(e) => setLang(e.target.value)}
      />
      <button onClick={handleProcess} disabled={loading}>
        {loading ? "Processing..." : "Post"}
      </button>
    </div>

    <div className="feed">
      {results.length === 0 && <p style={{ textAlign: "center" }}>No content yet.</p>}
      {results.map(([url, data]) => (
        <div key={url} className="post-card">
          <p className="post-url">🔗 {url}</p>
          <p className="post-summary">{data.summary}</p>

          {data.translation &&
            (data.translation_type === "ASL" || data.translation_lang === "ASL") && (
              <div className="post-translation-video">
                <p>🤟 ASL Video:</p>
                <video
                  controls
                  width="100%"
                  src={`http://localhost:5000/api/video?path=${encodeURIComponent(
                    data.translation
                  )}`}
                />
              </div>
            )}

          {data.translation &&
            data.translation_type !== "ASL" &&
            data.translation_lang !== "ASL" && (
              <div className="post-translation-audio">
                <p>
                  🌍{" "}
                  {data.translation_lang.charAt(0).toUpperCase() +
                    data.translation_lang.slice(1)}{" "}
                  Audio:
                </p>
                <audio controls>
                  <source
                    src={`http://localhost:5000/api/audio?path=${encodeURIComponent(
                      data.translation
                    )}`}
                    type="audio/mpeg"
                  />
                </audio>
              </div>
            )}
        </div>
      ))}
    </div>
  </div>
</div>
  );
}
