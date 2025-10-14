def normalize_data(data):
    # Mapear cabeçalhos divergentes
    header_mapping = {
        "Qtd. de Recursos": "Qde de Recursos",
        "Qde Recursos": "Qde de Recursos",
        "Quantidade de Recursos": "Qde de Recursos",
        "HH": "HH",
        "Horas": "Horas",
        "Fornecedor": "Fornecedor",
        "Perfil": "Perfil",
        "Alocação (meses)": "Alocação (meses)",
        "Status": "Status",
        "Classificação": "Classificação",
        "Total": "Total",
    }

    # Normalizar cabeçalhos
    normalized_data = []
    for row in data:
        normalized_row = {}
        for key, value in row.items():
            normalized_key = header_mapping.get(key.strip(), key.strip())
            normalized_row[normalized_key] = value if value else 0
        normalized_data.append(normalized_row)

    return normalized_data

def detect_header_row(sheet):
    # Calcular densidade de strings não nulas por linha
    densities = [
        sum(1 for cell in row if cell is not None and str(cell).strip())
        for row in sheet.iter_rows(values_only=True)
    ]
    # Retornar índice da linha com maior densidade
    return densities.index(max(densities)) + 1

@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        if file.filename.endswith('.xlsx'):
            workbook = load_workbook(file)

            # Usar fuzzy matching para encontrar a aba "Detalhes Técnicos"
            target_sheet = "detalhes técnicos"
            best_match = max(
                workbook.sheetnames,
                key=lambda name: fuzz.ratio(name.lower(), target_sheet)
            )

            if fuzz.ratio(best_match.lower(), target_sheet) < 80:
                return jsonify({'error': 'Sheet "Detalhes Técnicos" not found in Excel file'}), 400

            sheet = workbook[best_match]

            # Converter a aba inteira para JSON com todas as colunas
            headers = [cell.value for cell in sheet[1]]
            sheet_data = [
                {headers[i]: row[i] for i in range(len(headers))}
                for row in sheet.iter_rows(min_row=2, values_only=True)
            ]

            return jsonify({'message': 'Sheet converted successfully', 'data': sheet_data}), 200

        else:
            return jsonify({'error': 'Unsupported file format. Only .xlsx files are supported.'}), 400

    except Exception as e:
        logging.exception("Error processing the file")
        return jsonify({'error': str(e)}), 500

@app.route('/fornecedores', methods=['GET'])
def get_fornecedores():
    fornecedores = list(collection.find({}, {'_id': 0}))  # Exclui o campo `_id` da resposta
    return jsonify(fornecedores)

@app.route('/upload-json', methods=['POST'])
def upload_json():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Normalizar os dados
        normalized_data = normalize_data(data)

        # Inserção em lote no MongoDB
        if isinstance(normalized_data, list) and normalized_data:
            result = collection.insert_many(normalized_data)
            for doc, inserted_id in zip(normalized_data, result.inserted_ids):
                doc['_id'] = str(inserted_id)  # Converte ObjectId para string

            return jsonify({'message': 'Data uploaded successfully', 'data': normalized_data}), 200
        else:
            return jsonify({'error': 'Invalid JSON format. Expected a list of objects.'}), 400

    except Exception as e:
        logging.exception("Error processing the JSON data")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)