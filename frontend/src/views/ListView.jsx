import React, { useEffect, useState } from "react";
import axios from "axios";

// Mapa único para normalização de fornecedores
const manualMap = {
  // HITSS
  hitss: "hitss",
  hitts: "hitss",
  globalhitss: "hitss",
  // NTTDATA
  nttdata: "nttdata",
  ntt: "nttdata",
  "ntt..": "nttdata",
  // MJV
  mjv: "mjv",
  mjvtechnologyinnovation: "mjv",
  mjvsolucoemtecnologialtda: "mjv",
  mjvtecnologiaeinovacao: "mjv",
  mjvsolucoemtecnologia: "mjv",
  mjvsolucoesemtecnologialtda: "mjv",
  mjvsolucoesemtecnologia: "mjv",
  // Variações visuais
  "mjv technology & innovation": "mjv",
  "mjv soluções em tecnologia ltda": "mjv",
  // ATOS
  atos: "atos",
  atosajustedarc1008549873pedidoemitido5500508154: "atos",
  atosajustedarc100854987pedidoemitido5500508154: "atos",
  "atos ajuste da rc 100854987/3 pedido emitido 5500508154": "atos",
  // M4
  m4: "m4",
  m4po5500509779emitidaem1106: "m4",
  "m4 po - 5500509779 - emitida em 11/06": "m4",
  // Adicione outros agrupamentos especiais conforme necessário
};

function SupplierRow({ s, highlight }) {
  const [open, setOpen] = useState(false);
  const detalhes = Array.isArray(s.detalhes) ? s.detalhes : [];
  return (
    <div className="card">
      <div className="supplier-row">
        <div className="supplier-name">
          <div
            className="expand"
            onClick={() => setOpen(!open)}
            style={{ fontSize: 18 }}
          >
            {open ? "▾" : "▸"}
          </div>
          <div>
            <div style={{ fontWeight: 600 }}>{s.fornecedor}</div>
            <div className="muted" style={{ fontSize: 12 }}>
              {detalhes.length} entradas
            </div>
          </div>
        </div>
        <div
          className="supplier-total"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            justifyContent: "flex-end",
            minWidth: 320,
            gap: 0,
            fontSize: 15,
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              alignItems: "flex-start",
              justifyContent: "flex-start",
              background: "#f5f5f5",
              borderRadius: 8,
              padding: "6px 16px",
              boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
              minWidth: 260,
              width: "fit-content",
            }}
          >
            <span style={{ fontWeight: 600, color: "#222", fontSize: 15 }}>
              {Number(s.total_horas || 0).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}{" "}
              horas
            </span>
            <span style={{ fontWeight: 600, color: "#888", margin: "0 8px" }}>
              |
            </span>
            <span
              style={{
                fontWeight: 700,
                color: "#fff",
                background: "#c60000",
                borderRadius: 6,
                padding: "2px 14px",
                fontSize: 18,
                boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
              }}
            >
              R${" "}
              {Number(s.total).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
        </div>
      </div>
      {open && detalhes.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <table className="details-table">
            <thead>
              <tr>
                <th>Fornecedor</th>
                <th>Perfil</th>
                <th>Horas</th>
                <th>H/H</th>
                <th>Alocação (meses)</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {detalhes.map((d, i) => (
                <tr key={i}>
                  <td>{d.Fornecedor ?? s.fornecedor ?? "-"}</td>
                  <td>{d.Perfil ?? d.perfil ?? "-"}</td>
                  <td>
                    {d.Horas !== undefined && d.Horas !== null
                      ? Math.round(d.Horas)
                      : d.hora !== undefined && d.hora !== null
                      ? Math.round(d.hora)
                      : "-"}
                  </td>
                  <td>
                    {d.HH !== undefined && d.HH !== null
                      ? Math.round(d.HH)
                      : d.hh !== undefined && d.hh !== null
                      ? Math.round(d.hh)
                      : "-"}
                  </td>
                  <td>{d["Alocação (meses)"] ?? d.alocacao_meses ?? "-"}</td>
                  <td>
                    R${" "}
                    {Number(d.Total ?? d.valor_total ?? 0).toLocaleString(
                      "pt-BR",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 8, fontSize: 12 }} className="muted">
            Upload ID: {s.upload_id || "-"}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ListView({ fornecedores, refresh }) {
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("nome");
  // Filtro de busca por nome do fornecedor, sem ignorar total zero ou NaN
  let filtered = fornecedores.filter((f) => {
    const nome = (f.fornecedor || "").toLowerCase();
    if (!nome || nome === "fornecedor") return false;
    return nome.includes(q.toLowerCase());
  });

  // Ordenação
  filtered = [...filtered];
  if (sort === "nome") {
    filtered.sort((a, b) =>
      (a.fornecedor || "").localeCompare(b.fornecedor || "")
    );
  } else if (sort === "valor") {
    filtered.sort((a, b) => (b.total || 0) - (a.total || 0));
  } else if (sort === "horas") {
    filtered.sort((a, b) => (b.total_horas || 0) - (a.total_horas || 0));
  }

  return (
    <div>
      <div
        className="search"
        style={{
          marginBottom: 18,
          display: "flex",
          gap: 12,
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <input
          placeholder="Buscar fornecedor..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #e3e7ee",
            width: 320,
          }}
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ fontSize: 14, color: '#666' }}>Filtrar por:</div>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: 8,
              border: "1px solid #e3e7ee",
              background: '#fff'
            }}
          >
            <option value="nome">Nome</option>
            <option value="valor">Valor total</option>
            <option value="horas">Horas</option>
          </select>
        </div>

        <div className="muted">{filtered.length} encontrados</div>
      </div>
      {filtered.length === 0 ? (
        <div className="empty">Nenhum fornecedor encontrado.</div>
      ) : (
        filtered.map((s, i) => (
          <SupplierRow
            key={i}
            s={{
              ...s,
              detalhes: Array.isArray(s.detalhes) ? s.detalhes : [],
            }}
          />
        ))
      )}
    </div>
  );
}
