import React from "react";

export default function ResumoGastosView({ fornecedores }) {
  const totalGasto = fornecedores.reduce((acc, f) => acc + (f.total || 0), 0);
  let tipoValor = "";
  if (totalGasto >= 1_000_000_000) {
    tipoValor = "bilhões**";
  } else if (totalGasto >= 1_000_000) {
    tipoValor = "milhões**";
  } else if (totalGasto >= 1_000) {
    tipoValor = "mil";
  } else {
    tipoValor = "real";
  }

  return (
    <div
      className="card"
      style={{
        marginBottom: 24,
        textAlign: "center",
        background: "#c60000",
        color: "#fff",
        border: "none",
        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
      }}
    >
      <h2 style={{ color: "#fff" }}>Resumo Geral</h2>
      <div style={{ fontSize: 22, margin: "12px 0" }}>
        <strong>Total em R$:</strong>{" "}
        {totalGasto.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}{" "}
        <span style={{ fontSize: 18, fontWeight: 400 }}>({tipoValor})</span>
      </div>
    </div>
  );
}
