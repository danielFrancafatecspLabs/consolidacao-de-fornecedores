import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import UploadView from "./views/UploadView";
import ListView from "./views/ListView";
import Dashboard from "./views/Dashboard";
import axios from "axios";

export default function App() {
  const [view, setView] = useState("upload");
  const [fornecedores, setFornecedores] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [raw, setRaw] = useState(null);
  const [showDebug, setShowDebug] = useState(false);

  const fetchList = async () => {
    setLoading(true);
    setError(null);
    try {
      // use 127.0.0.1 to avoid potential hostname resolution/cors oddities
      const res = await axios.get(
        "https://consolidacao-de-fornecedores.onrender.com/fornecedores"
      );
      setFornecedores(res.data || []);
      setRaw(res.data || null);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data || err.message || String(err));
      setFornecedores([]);
      setRaw(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!loading) {
      fetchList();
    }
  }, []);

  const filtered = fornecedores.filter((f) =>
    (f.fornecedor || "").toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="app-root">
      <Sidebar view={view} setView={setView} />
      <main className="main-area">
        <div className="topbar">
          <div className="search">
            <input
              placeholder="Buscar fornecedor..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
            <div className="muted">{filtered.length} encontrados</div>
          </div>
          <div className="actions">
            <button className="btn secondary" onClick={() => setView("upload")}>
              Novo Upload
            </button>
            <button className="btn" onClick={fetchList}>
              {loading ? "Carregando..." : "Atualizar"}
            </button>
            <button
              className="btn secondary"
              onClick={() => setShowDebug((s) => !s)}
            >
              {showDebug ? "Esconder debug" : "Mostrar debug"}
            </button>
          </div>
        </div>

        {error && (
          <div
            className="card"
            style={{
              background: "#fff3f3",
              border: "1px solid #ffd6d6",
              color: "#7a0000",
            }}
          >
            <strong>Erro ao buscar fornecedores:</strong>{" "}
            {JSON.stringify(error)}
          </div>
        )}

        {view === "upload" && <UploadView onUpload={fetchList} />}
        {view === "list" && (
          <ListView fornecedores={filtered} refresh={fetchList} />
        )}
        {view === "dashboard" && <Dashboard fornecedores={fornecedores} />}

        {showDebug && (
          <div className="card" style={{ marginTop: 16 }}>
            <h3>Debug: resposta bruta da API</h3>
            {loading ? (
              <div className="muted">Carregando...</div>
            ) : raw ? (
              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  maxHeight: 300,
                  overflow: "auto",
                }}
              >
                {JSON.stringify(raw, null, 2)}
              </pre>
            ) : (
              <div className="muted">Nenhum dado recebido.</div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
