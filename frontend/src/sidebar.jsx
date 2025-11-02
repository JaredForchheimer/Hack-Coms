import React from "react";
import "./sidebar.css";

export default function Sidebar() {
  return (
    <div className="sidebar">
      <h2 className="sidebar-header">Menu</h2>
      <ul className="sidebar-menu">
        <li className="sidebar-item">Sources</li>
        <li className="sidebar-item">Upload</li>
      </ul>
    </div>
  );
}
