import React from "react";
import { FaUpload, FaList, FaChartBar } from "react-icons/fa";

export default function Sidebar({ view, setView }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: 8,
            background: "linear-gradient(45deg,#ff4d4d,#c60000)",
          }}
        ></div>
        <div>
          <h1>Claro Dashboard</h1>
          <small>Consolidação Fornecedores</small>
        </div>
      </div>
      <nav>
        <div
          className={`sidebar-item ${view === "upload" ? "active" : ""}`}
          onClick={() => setView("upload")}
        >
          <FaUpload className="icon" /> Novo Upload
        </div>
        <div
          className={`sidebar-item ${view === "list" ? "active" : ""}`}
          onClick={() => setView("list")}
        >
          <FaList className="icon" /> Lista de Fornecedores
        </div>
        <div
          className={`sidebar-item ${view === "dashboard" ? "active" : ""}`}
          onClick={() => setView("dashboard")}
        >
          <FaChartBar className="icon" /> Dashboard
        </div>
      </nav>
      <div style={{ flex: 1 }} />
      <div style={{ fontSize: 12, color: "#9aa3b2" }}>v0.1 • interno</div>
    </aside>
  );
}
