import React from "react";
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
      name: f.fornecedor,
      total: f.total,
    }));

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  const bestSupplier = data.length > 0 ? data[0] : null;

  return (
    <div className="dashboard">
      <h2>Dashboard de Fornecedores</h2>
      <div className="highlight">
        <h3>Melhor Fornecedor</h3>
        <div className="best-supplier">
          {bestSupplier ? (
            <>
              <strong>{bestSupplier.name}</strong> com custo-benefício de R${" "}
              {Number(
                bestSupplier.total / (bestSupplier.entries || 1)
              ).toLocaleString("pt-BR", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </>
          ) : (
            <span>Nenhum fornecedor válido encontrado.</span>
          )}
        </div>
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
