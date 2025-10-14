import React, { useState, useEffect } from "react";
import axios from "axios";
import * as XLSX from "xlsx";

// Componentização da tabela para renderizar os dados processados
function DataTable({ data, filters }) {
  const applyFilters = () => {
    return data.filter((row) => {
      return Object.entries(filters).every(([key, value]) =>
        value ? row[key]?.toString().includes(value) : true
      );
    });
  };

  return (
    <table>
      <thead>
        <tr>
          {data.length > 0 &&
            Object.keys(data[0]).map((key) => <th key={key}>{key}</th>)}
        </tr>
      </thead>
      <tbody>
        {applyFilters().map((row, index) => (
          <tr key={index}>
            {Object.keys(row).map((key) => (
              <td key={key}>
                {typeof row[key] === "object" && row[key] !== null
                  ? JSON.stringify(row[key]) // Converte objetos em string
                  : row[key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function UploadView({ onUpload }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({});
  const [drag, setDrag] = useState(false);

  useEffect(() => {
    // Fetch fornecedores from the backend
    const fetchFornecedores = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8001/fornecedores");
        setData(response.data);
      } catch (error) {
        console.error("Erro ao buscar fornecedores:", error);
        alert(
          "Erro ao buscar fornecedores. Verifique o console para mais detalhes."
        );
      }
    };

    fetchFornecedores();
  }, []);

  const processFilesToJson = (files) => {
    return Promise.all(
      files.map(
        (file) =>
          new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
              const data = new Uint8Array(e.target.result);
              const workbook = XLSX.read(data, { type: "array" });

              // Procurar a aba "Detalhes Técnicos"
              const sheetName = workbook.SheetNames.find(
                (name) =>
                  name.trim().toLowerCase() === "anexo 1 - detalhes técnicos"
              );

              if (!sheetName) {
                reject(
                  `Aba 'ANEXO 1 - Detalhes Técnicos' não encontrada no arquivo ${file.name}.`
                );
                return;
              }

              const sheet = workbook.Sheets[sheetName];
              const json = XLSX.utils.sheet_to_json(sheet);
              resolve(json);
            };
            reader.onerror = (err) => reject(err);
            reader.readAsArrayBuffer(file);
          })
      )
    );
  };

  const submit = async () => {
    if (files.length === 0) {
      alert("Nenhum arquivo selecionado.");
      return;
    }

    try {
      setLoading(true);
      const jsonDataArray = await processFilesToJson(files);

      // Consolidar dados dinamicamente com todas as colunas
      const consolidatedData = jsonDataArray.flatMap((jsonData) =>
        jsonData.map((row) => {
          const dynamicRow = {};
          Object.keys(row).forEach((key) => {
            dynamicRow[key] = row[key] || "";
          });
          return dynamicRow;
        })
      );

      setData(consolidatedData);
      alert("Upload realizado com sucesso.");
    } catch (err) {
      console.error("Erro ao processar os arquivos:", err);
      alert("Erro: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload de Documentos</h2>
      <div className="card">
        <div
          className={`file-input ${drag ? "drag" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDrag(true);
          }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            setFiles(Array.from(e.dataTransfer.files));
          }}
        >
          <div style={{ fontWeight: 700 }}>
            Arraste e solte ou clique para selecionar
          </div>
          <div className="muted">
            Procure a aba <strong>Detalhes Técnicos</strong> no arquivo .xlsx
          </div>
          <div style={{ marginTop: 12 }}>
            <input
              style={{ width: "100%" }}
              type="file"
              accept=".xlsx"
              multiple
              onChange={(e) => setFiles(Array.from(e.target.files))}
            />
          </div>
        </div>
        <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
          <button
            className="btn"
            onClick={submit}
            disabled={loading || files.length === 0}
          >
            {loading ? "Enviando..." : "Enviar"}
          </button>
          <button className="btn secondary" onClick={() => setFiles([])}>
            Limpar
          </button>
        </div>
      </div>

      <div>
        <h3>Filtros</h3>
        <div>
          {Object.keys(filters).map((key) => (
            <input
              key={key}
              type="text"
              placeholder={`Filtrar por ${key}`}
              value={filters[key] || ""}
              onChange={(e) =>
                setFilters({ ...filters, [key]: e.target.value })
              }
            />
          ))}
        </div>
      </div>

      <div>
        <h3>Dados Processados</h3>
        <DataTable data={data} filters={filters} />
      </div>
    </div>
  );
}
