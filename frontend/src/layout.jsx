import React, { useState } from "react";
import Sidebar from "./sidebar";
import App from "./App";
import SourcesPage from "./sources";
import UploadPage from "./upload";
import "./layout.css";

export default function Layout() {
  const [activePage, setActivePage] = useState("feed");

  return (
    <div className="layout">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      <div className="main-content">
        {activePage === "feed" && <App />}
        {activePage === "sources" && <SourcesPage />}
        {activePage === "upload" && <UploadPage />}
      </div>
    </div>
  );
}
