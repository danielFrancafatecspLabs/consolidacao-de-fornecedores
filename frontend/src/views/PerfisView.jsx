import React from "react";
import normalizeFornecedorDisplay from "../utils/normalizeFornecedor";

export default function PerfisView({ fornecedores }) {
  // Extrai todos os perfis de todos os fornecedores
  const perfis = [];
  fornecedores.forEach((f) => {
    if (Array.isArray(f.detalhes)) {
      f.detalhes.forEach((d) => {
        perfis.push({
          fornecedor: f.fornecedor,
          perfil: d.perfil ?? "-",
          valor_total: d.valor_total ?? d.total ?? 0,
        });
      });
    }
  });

  return (
    <div style={{ padding: "24px 0" }}>
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
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 24,
          justifyContent: "center",
        }}
      >
        {perfis.length === 0 ? (
          <div className="empty">Nenhum perfil encontrado.</div>
        ) : (
          perfis.map((p, i) => (
            <div
              key={i}
              className="card"
              style={{
                minWidth: 260,
                maxWidth: 320,
                background: "#fff",
                borderRadius: 12,
                boxShadow: "0 4px 16px rgba(11,22,39,0.08)",
                padding: "22px 18px 18px 18px",
                position: "relative",
                border: "1px solid #f1f5f9",
                transition: "box-shadow 0.2s",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  marginBottom: 10,
                }}
              >
                <span
                  style={{
                    display: "inline-block",
                    width: 36,
                    height: 36,
                    borderRadius: "50%",
                    background: "var(--bg)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 20,
                    color: "var(--primary)",
                    fontWeight: 700,
                    boxShadow: "0 2px 8px rgba(230,0,0,0.08)",
                  }}
                >
                  {normalizeFornecedorDisplay(p.fornecedor)[0]?.toUpperCase()}
                </span>
                <div>
                  <div
                    style={{
                      fontWeight: 600,
                      fontSize: 16,
                      color: "var(--accent)",
                    }}
                  >
                    {normalizeFornecedorDisplay(p.fornecedor)}
                  </div>
                  <div
                    style={{
                      fontSize: 13,
                      color: "var(--muted)",
                      marginTop: 2,
                    }}
                  >
                    {p.perfil}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 15, color: "#333", marginBottom: 8 }}>
                <span style={{ fontWeight: 500, color: "var(--muted)" }}>
                  Valor Total:
                </span>
                <span
                  style={{
                    fontWeight: 700,
                    color: "var(--primary)",
                    marginLeft: 8,
                  }}
                >
                  R${" "}
                  {Number(p.valor_total).toLocaleString("pt-BR", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>
              <div style={{ fontSize: 15, color: "#333", marginBottom: 8 }}>
                <span style={{ fontWeight: 500, color: "var(--muted)" }}>
                  Total de Horas:
                </span>
                <span
                  style={{
                    fontWeight: 700,
                    color: "#1976d2",
                    marginLeft: 8,
                  }}
                >
                  {typeof f.total_horas !== "undefined"
                    ? Number(f.total_horas).toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })
                    : "-"}
                </span>
              </div>
              <div style={{ position: "absolute", top: 12, right: 18 }}>
                <span
                  style={{
                    background: "#e8f5e9",
                    color: "#2e7d32",
                    borderRadius: 8,
                    padding: "2px 10px",
                    fontSize: 12,
                    fontWeight: 600,
                  }}
                >
                  Perfil
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
