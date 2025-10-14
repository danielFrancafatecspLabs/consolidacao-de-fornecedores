import React, { useEffect, useState } from "react";
import axios from "axios";

function SupplierRow({ s, highlight }) {
  const [open, setOpen] = useState(false);
  const detalhes = Array.isArray(s.detalhes) ? s.detalhes : [];
  return (
    <div
      className="card"
      key={s._id}
      style={{
        marginBottom: 12,
        border: highlight ? "2px solid green" : "none",
      }}
    >
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
        <div className="supplier-total">
          R${" "}
          {Number(s.total).toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
          })}
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
                  <td>{s.fornecedor}</td>
                  <td>{d.perfil ?? "-"}</td>
                  <td>
                    {d.hora !== undefined && d.hora !== null
                      ? Math.round(d.hora)
                      : "-"}
                  </td>
                  <td>
                    {d.hh !== undefined && d.hh !== null
                      ? Math.round(d.hh)
                      : "-"}
                  </td>
                  <td>{d.alocacao_meses ?? "-"}</td>
                  <td>{d.classificacao ?? "-"}</td>
                  <td>
                    R${" "}
                    {Number(d.valor_total || 0).toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
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
  const sortedFornecedores = fornecedores
    .filter((f) => f.total !== null && f.total !== undefined && f.total > 0)
    .sort((a, b) => a.total - b.total);

  return (
    <div>
      <h2>Fornecedores</h2>

      <div style={{ marginTop: 12 }}>
        {sortedFornecedores.length === 0 && (
          <div className="card empty">
            Nenhum fornecedor cadastrado ainda. Faça um upload para começar.
          </div>
        )}
        {sortedFornecedores.map((f, index) => (
          <SupplierRow
            key={f._id || f.fornecedor}
            s={f}
            highlight={index === 0}
          />
        ))}
      </div>
    </div>
  );
}
