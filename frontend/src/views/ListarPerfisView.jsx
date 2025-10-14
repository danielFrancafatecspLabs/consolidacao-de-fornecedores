import React, { useEffect, useState } from "react";

const ListarPerfisView = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8001/perfis")
      .then((res) => res.json())
      .then((result) => {
        setData(result.data || []);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ background: "#f7f8fa", minHeight: "100vh", padding: 24 }}>
      <h2 style={{ color: "#c60000", marginBottom: 24 }}>Listar Perfis</h2>
      {loading ? (
        <p style={{ color: "#c60000" }}>Carregando...</p>
      ) : (
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            background: "#fff",
            borderRadius: 8,
            boxShadow: "0 2px 8px #0001",
          }}
        >
          <thead style={{ background: "#ffeaea" }}>
            <tr>
              <th style={{ padding: 8, color: "#c60000" }}>Fornecedor</th>
              <th style={{ padding: 8, color: "#c60000" }}>Perfil</th>
              <th style={{ padding: 8, color: "#c60000" }}>Horas</th>
              <th style={{ padding: 8, color: "#c60000" }}>H/H</th>
              <th style={{ padding: 8, color: "#c60000" }}>Valor Total</th>
            </tr>
          </thead>
          <tbody>
            {data
              .filter((item) => item.fornecedor !== "Fornecedor")
              .map((item, idx) => {
                // Destacar linhas com problemas
                const isProblem = !item.perfil || item.perfil === "Perfil";
                return (
                  <tr
                    key={idx}
                    style={isProblem ? { background: "#ffeaea" } : {}}
                  >
                    <td style={{ padding: 8 }}>{item.fornecedor}</td>
                    <td style={{ padding: 8 }}>{item.perfil ?? "-"}</td>
                    <td style={{ padding: 8, textAlign: "right" }}>
                      {item.hora !== undefined && item.hora !== null
                        ? Math.round(item.hora)
                        : "-"}
                    </td>
                    <td style={{ padding: 8, textAlign: "right" }}>
                      {item.hh !== undefined && item.hh !== null
                        ? Math.round(item.hh)
                        : "-"}
                    </td>
                    <td
                      style={{
                        padding: 8,
                        textAlign: "right",
                        color: "#c60000",
                        fontWeight: 600,
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
              })}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ListarPerfisView;
