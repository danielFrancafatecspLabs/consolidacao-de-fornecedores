import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ListView from "./views/ListView";
import ResumoGastosView from "./views/ResumoGastosView";
import axios from "axios";

export default function App() {
  const [view, setView] = useState("list");
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
      // Alterna entre dev e prod automaticamente
      const backendUrl =
  (import.meta.env.VITE_API_URL || "https://consolidacao-de-fornecedores-7.onrender.com") + "/fornecedores";
      const res = await axios.get(backendUrl);
      if (Array.isArray(res.data.data)) {
        setFornecedores(res.data.data);
      } else {
        setFornecedores([]);
      }
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

        {/* Apenas lista e resumo, sem upload */}
        <ResumoGastosView fornecedores={fornecedores} />
        <ListView fornecedores={filtered} refresh={fetchList} />

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
