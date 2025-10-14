import React from "react";

export default function PerfisView({ fornecedores }) {
  // Extrai todos os perfis de todos os fornecedores
  const perfis = [];
  fornecedores.forEach((f) => {
    if (Array.isArray(f.detalhes)) {
      f.detalhes.forEach((d) => {
        perfis.push({
          fornecedor: f.fornecedor,
          perfil: d.perfil ?? "-",
          valor_total: d.valor_total ?? 0,
        });
      });
    }
  });

  return (
    <div>
      <h2>Listar Perfis</h2>
      <table className="details-table" style={{ marginTop: 16 }}>
        <thead>
          <tr>
            <th>Fornecedor</th>
            <th>Perfil</th>
            <th>Valor Total</th>
          </tr>
        </thead>
        <tbody>
          {perfis.map((p, i) => (
            <tr key={i}>
              <td>{p.fornecedor}</td>
              <td>{p.perfil}</td>
              <td>
                R${" "}
                {Number(p.valor_total).toLocaleString("pt-BR", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
