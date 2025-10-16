import React, { useEffect, useState } from "react";

const ListarPerfisView = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8001/fornecedores")
      .then((res) => res.json())
      .then((result) => {
        setData(result.data || []);
        setLoading(false);
      });
  }, []);

  // Filtro de busca por fornecedor ou perfil
  const filtered = data.filter(
    (item) =>
      (item.fornecedor || "").toLowerCase().includes(q.toLowerCase()) ||
      (item.perfil || "").toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div style={{ background: "#f7f8fa", minHeight: "100vh", padding: 24 }}>
      <h2
        style={{
          textAlign: "center",
          color: "var(--accent)",
          marginBottom: 32,
        }}
      >
        Perfis dos Fornecedores
      </h2>
      <div
        className="search"
        style={{
          marginBottom: 18,
          display: "flex",
          gap: 12,
          justifyContent: "center",
        }}
      >
        <input
          placeholder="Buscar fornecedor ou perfil..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #e3e7ee",
            width: 320,
          }}
        />
        <div className="muted">{filtered.length} encontrados</div>
      </div>
      {loading ? (
        <div className="empty">Carregando...</div>
      ) : (
        <table
          className="details-table"
          style={{
            width: "100%",
            background: "#fff",
            borderRadius: 10,
            boxShadow: "0 2px 8px #0001",
            overflow: "hidden",
          }}
        >
          <thead style={{ background: "#f4f6f8" }}>
            <tr>
              <th
                style={{
                  color: "var(--muted)",
                  fontWeight: 600,
                  padding: "12px 8px",
                }}
              >
                Fornecedor
              </th>
              <th
                style={{
                  color: "var(--muted)",
                  fontWeight: 600,
                  padding: "12px 8px",
                }}
              >
                Perfil
              </th>
              <th
                style={{
                  color: "var(--muted)",
                  fontWeight: 600,
                  padding: "12px 8px",
                }}
              >
                Horas
              </th>
              <th
                style={{
                  color: "var(--muted)",
                  fontWeight: 600,
                  padding: "12px 8px",
                }}
              >
                H/H
              </th>
              <th
                style={{
                  color: "var(--muted)",
                  fontWeight: 600,
                  padding: "12px 8px",
                }}
              >
                Valor Total
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty">
                  Nenhum perfil encontrado.
                </td>
              </tr>
            ) : (
              filtered
                .filter((item) => item.fornecedor !== "Fornecedor")
                .map((item, idx) => {
                  const isProblem = !item.perfil || item.perfil === "Perfil";
                  return (
                    <tr
                      key={idx}
                      style={{ background: idx % 2 === 0 ? "#fff" : "#f7f8fa" }}
                    >
                      <td
                        style={{
                          padding: "10px 8px",
                          fontWeight: 600,
                          color: "var(--accent)",
                        }}
                      >
                        {item.fornecedor}
                      </td>
                      <td
                        style={{
                          padding: "10px 8px",
                          color: isProblem ? "#c60000" : "var(--muted)",
                        }}
                      >
                        {item.perfil ?? "-"}
                      </td>
                      <td
                        style={{
                          padding: "10px 8px",
                          textAlign: "right",
                          color: "#0a2540",
                        }}
                      >
                        {item.hora !== undefined && item.hora !== null
                          ? Math.round(item.hora)
                          : "-"}
                      </td>
                      <td
                        style={{
                          padding: "10px 8px",
                          textAlign: "right",
                          color: "#0a2540",
                        }}
                      >
                        {item.hh !== undefined && item.hh !== null
                          ? Math.round(item.hh)
                          : "-"}
                      </td>
                      <td
                        style={{
                          padding: "10px 8px",
                          textAlign: "right",
                          fontWeight: 700,
                          color: "var(--primary)",
                        }}
                      >
                        R${" "}
                        {Number(item.valor_total || 0).toLocaleString("pt-BR", {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                    </tr>
                  );
                })
            )}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ListarPerfisView;
