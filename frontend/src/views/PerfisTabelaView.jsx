import React from "react";

export default function PerfisTabelaView({ fornecedores }) {
  // Extrai todos os perfis válidos de todos os fornecedores
  const perfis = [];
  fornecedores.forEach((f) => {
    if (Array.isArray(f.detalhes)) {
      f.detalhes.forEach((d) => {
        // Só inclui se perfil não for nulo, vazio ou branco
        if (d.perfil && String(d.perfil).trim()) {
          perfis.push({
            perfil: d.perfil,
            fornecedor: f.fornecedor,
            horas: d.hora ?? null,
            hh: d.hh ?? null,
            valor_total: d.valor_total ?? null,
          });
        }
      });
    }
  });

  return (
    <div>
      <h2>Lista de Perfil</h2>
      <table className="details-table" style={{ marginTop: 16 }}>
        <thead>
          <tr>
            <th>Perfil</th>
            <th>Fornecedor</th>
            <th>Horas</th>
            <th>H/H</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {perfis.map((p, i) => (
            <tr key={i}>
              <td>{p.perfil}</td>
              <td>{p.fornecedor}</td>
              <td>
                {p.horas !== null && p.horas !== undefined
                  ? Math.round(p.horas)
                  : null}
              </td>
              <td>
                {p.hh !== null && p.hh !== undefined ? Math.round(p.hh) : null}
              </td>
              <td>
                {p.valor_total !== null && p.valor_total !== undefined
                  ? `R$ ${Number(p.valor_total).toLocaleString("pt-BR", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}`
                  : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
