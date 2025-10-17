import React from "react";
import normalizeFornecedorDisplay from "../utils/normalizeFornecedor";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const Dashboard = ({ fornecedores }) => {
  const data = fornecedores
    .filter((f) => f && f.fornecedor && f.total)
    .map((f) => ({
      name: normalizeFornecedorDisplay(f.fornecedor),
      total: f.total,
      detalhes: f.detalhes || [],
    }));

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const bestSupplier = data.length > 0 ? data[0] : null;
  const bestSupplierDetails =
    bestSupplier && bestSupplier.detalhes ? bestSupplier.detalhes : [];

  return (
    <div className="dashboard">
      <h2>Dashboard de Fornecedores</h2>
      <div className="highlight">
        <h3>Melhor Fornecedor</h3>
        <div className="best-supplier">
          {bestSupplier ? (
            <>
              <strong>{bestSupplier.name}</strong> com custo-benefício de R${" "}
              {Number(bestSupplier.total).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </>
          ) : (
            <span>Nenhum fornecedor válido encontrado.</span>
          )}
        </div>
        {/* Memória de cálculo do melhor fornecedor */}
        {bestSupplierDetails.length > 0 && (
          <div className="calculo-memoria" style={{ marginTop: 16 }}>
            <h4>Memória de cálculo</h4>
            <table className="details-table">
              <thead>
                <tr>
                  <th>Perfil</th>
                  <th>Horas</th>
                  <th>H/H</th>
                  <th>Qtde de Recursos</th>
                  <th>Alocação (meses)</th>
                  <th>Status</th>
                  <th>Classificação</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {bestSupplierDetails.map((d, i) => (
                  <tr key={i}>
                    <td>{d.perfil ?? "-"}</td>
                    <td>{d.hora ?? "-"}</td>
                    <td>{d.hh ?? "-"}</td>
                    <td>{d.qtde_recursos ?? "-"}</td>
                    <td>{d.alocacao_meses ?? "-"}</td>
                    <td>{d.status ?? "-"}</td>
                    <td>{d.classificacao ?? "-"}</td>
                    <td>
                      R{" "}
                      {Number(d.valor_total || 0).toLocaleString("pt-BR", {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="charts">
        <div className="chart">
          <h3>Comparação de Custos</h3>
          <BarChart
            width={500}
            height={300}
            data={data.filter((d) => d.total > 0)}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="total" fill="#8884d8" label={{ position: "top" }} />
          </BarChart>
        </div>
        <div className="chart">
          <h3>Distribuição de Fornecedores</h3>
          <PieChart width={400} height={400}>
            <Pie
              data={data.filter((d) => d.total > 0)}
              cx={200}
              cy={200}
              labelLine={false}
              label={({ name, percent }) =>
                `${name} (${(percent * 100).toFixed(0)}%)`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey="total"
            >
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
          </PieChart>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
