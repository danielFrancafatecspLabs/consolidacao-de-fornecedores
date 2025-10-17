import React, { useEffect, useState } from "react";
import axios from "axios";

// Hook para buscar total de horas por fornecedor
function useHorasPorFornecedor() {
  const [horas, setHoras] = useState({});
  useEffect(() => {
    const backendUrl =
      "https://consolidacao-de-fornecedores-7.onrender.com/fornecedores/horas";
    axios.get(backendUrl).then((res) => {
      const map = {};
      (res.data.data || []).forEach((item) => {
        // Normaliza e agrupa variações
        let nome = item.fornecedor
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "");
        nome = nome.replace(/[.,\-\s]/g, "").toLowerCase();
        const manualMap = {
          hitss: "hitss",
          hitts: "hitss",
          nttdata: "nttdata",
          "ntt..": "nttdata",
          ntt: "nttdata",
        };
        nome = manualMap[nome] || nome;
        map[nome] = (map[nome] || 0) + item.total_horas;
      });
      setHoras(map);
    });
  }, []);
  return horas;
}

function SupplierRow({ s, highlight }) {
  const [open, setOpen] = useState(false);
  const detalhes = Array.isArray(s.detalhes) ? s.detalhes : [];
  const horasPorFornecedor = useHorasPorFornecedor();
  // Normaliza o nome do fornecedor para buscar no mapa
  let nomeFornecedorNormalizado = (s.fornecedor || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
  nomeFornecedorNormalizado = nomeFornecedorNormalizado
    .replace(/[.,\-\s]/g, "")
    .toLowerCase();
  const manualMap = {
    hitss: "hitss",
    hitts: "hitss",
    nttdata: "nttdata",
    "ntt..": "nttdata",
    ntt: "nttdata",
  };
  nomeFornecedorNormalizado =
    manualMap[nomeFornecedorNormalizado] || nomeFornecedorNormalizado;
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
              {Number(
                horasPorFornecedor[nomeFornecedorNormalizado] || 0
              ).toLocaleString("pt-BR", {
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
                <th>Classificação</th>
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
                  <td>{d.Classificacao ?? d.classificacao ?? "-"}</td>
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
  // Filtro de busca por nome do fornecedor, sem ignorar total zero ou NaN
  const filtered = fornecedores.filter((f) => {
    const nome = (f.fornecedor || "").toLowerCase();
    if (!nome || nome === "fornecedor") return false;
    return nome.includes(q.toLowerCase());
  });

  return (
    <div>
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
