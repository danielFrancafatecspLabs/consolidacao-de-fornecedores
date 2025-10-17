import React, { useState } from "react";
import axios from "axios";

const UploadCSV = () => {
  const [data, setData] = useState([]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("/upload-csv", formData);
      setData(response.data.data);
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  return (
    <div>
      <h1>Upload CSV</h1>
      <input type="file" accept=".csv" onChange={handleFileUpload} />
      <table border="1">
        <thead>
          <tr>
            <th>Fornecedor</th>
            <th>Perfil</th>
            <th>Horas</th>
            <th>HH</th>
            <th>Qde de Recursos</th>
            <th>Alocação (meses)</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>{row.Fornecedor}</td>
              <td>{row.Perfil}</td>
              <td>{row.Horas}</td>
              <td>{row.HH}</td>
              <td>{row["Qde de Recursos"]}</td>
              <td>{row["Alocação (meses)"]}</td>
              <td>{row.Total}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UploadCSV;
