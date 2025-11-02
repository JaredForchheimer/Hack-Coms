import React from "react";
import ReactDOM from "react-dom/client";
import Layout from "./layout";  // <-- make sure this points to your Layout.jsx
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Layout />
  </React.StrictMode>
);
