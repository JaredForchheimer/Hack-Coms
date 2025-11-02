import React from "react";
import App from "./App";
import Sidebar from "./sidebar";
import "./layout.css";

export default function Layout() {
  return (
    <div className="layout">
      <Sidebar />
      <div className="main-content">
        <App />
      </div>
    </div>
  );
}
