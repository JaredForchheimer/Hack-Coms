import React from "react";
import "./sidebar.css";

export default function Sidebar({ activePage, setActivePage }) {
  const menuItems = [
    { label: "Home", key: "feed" },
    { label: "Sources", key: "sources" },
    { label: "Upload", key: "upload" },
  ];

  return (
    <div className="sidebar">
      <ul className="sidebar-menu">
        {menuItems.map((item) => (
          <li
            key={item.key}
            className={`sidebar-item ${activePage === item.key ? "active" : ""}`}
            onClick={() => setActivePage(item.key)}
          >
            {item.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
