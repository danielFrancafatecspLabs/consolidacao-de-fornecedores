import path from 'path';
import { parseAndValidateFornecedores } from '../utils/parseExcel.js';
import {
  getAllFornecedores,
  getFornecedoresHoras,
  insertSampleToDB,
} from '../services/fornecedoresService.js';

export async function getFornecedores(req, res) {
  try {
    let fornecedores = await getAllFornecedores();
    // Filtros automáticos via query params
    const { fornecedor, valorMin, valorMax, horasMin, horasMax, sort } =
      req.query;
    if (fornecedor) {
      fornecedores = fornecedores.filter((f) =>
        (f.fornecedor || '').toLowerCase().includes(fornecedor.toLowerCase()),
      );
    }
    if (valorMin) {
      fornecedores = fornecedores.filter(
        (f) => (f.total || 0) >= Number(valorMin),
      );
    }
    if (valorMax) {
      fornecedores = fornecedores.filter(
        (f) => (f.total || 0) <= Number(valorMax),
      );
    }
    if (horasMin) {
      fornecedores = fornecedores.filter(
        (f) => (f.total_horas || 0) >= Number(horasMin),
      );
    }
    if (horasMax) {
      fornecedores = fornecedores.filter(
        (f) => (f.total_horas || 0) <= Number(horasMax),
      );
    }
    // Agrupa fornecedores por nome normalizado
    const map = {};
    const manualMap = {
      // HITSS
      hitss: 'hitss',
      hitts: 'hitss',
      globalhitss: 'hitss',
      // NTTDATA
      nttdata: 'nttdata',
      ntt: 'nttdata',
      'ntt..': 'nttdata',
      // MJV
      mjv: 'mjv',
      mjvtechnologyinnovation: 'mjv',
      mjvsolucoemtecnologialtda: 'mjv',
      mjvtecnologiaeinovacao: 'mjv',
      mjvsolucoemtecnologia: 'mjv',
      mjvsolucoesemtecnologialtda: 'mjv',
      mjvsolucoesemtecnologia: 'mjv',
      'mjv technology & innovation': 'mjv',
      'mjv soluções em tecnologia ltda': 'mjv',
      // ATOS
      atos: 'atos',
      atosajustedarc1008549873pedidoemitido5500508154: 'atos',
      atosajustedarc100854987pedidoemitido5500508154: 'atos',
      'atos ajuste da rc 100854987/3 pedido emitido 5500508154': 'atos',
      // M4
      m4: 'm4',
      m4po5500509779emitidaem1106: 'm4',
      'm4 po - 5500509779 - emitida em 11/06': 'm4',
      // ENGINEERING
      engineering: 'engineering',
      engeering: 'engineering',
      enginnering: 'engineering',
      engineeringbrasil: 'engineering',
      engineeringdobrasil: 'engineering',
      engineeringdo: 'engineering',
      engeeringbrasil: 'engineering',
      engeeringdobrasil: 'engineering',
      // SITE BLINDADO
      siteblindado: 'siteblindado',
      siteblindadoltda: 'siteblindado',
    };
    for (const f of fornecedores) {
      let nome = (f.fornecedor || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
      nome = nome.replace(/[.,\-\s&]/g, '').toLowerCase();
      nome = manualMap[nome] || nome;
      if (!map[nome]) {
        map[nome] = {
          ...f,
          fornecedor: f.fornecedor,
          total_horas: f.total_horas || 0,
          detalhes: Array.isArray(f.detalhes) ? [...f.detalhes] : [],
        };
      } else {
        map[nome].total += f.total || 0;
        map[nome].total_horas =
          (map[nome].total_horas || 0) + (f.total_horas || 0);
        map[nome].detalhes = map[nome].detalhes.concat(
          Array.isArray(f.detalhes) ? f.detalhes : [],
        );
      }
    }
    let result = Object.values(map);
    // Ordenação
    if (sort === 'valor') {
      result = result.sort((a, b) => (b.total || 0) - (a.total || 0));
    } else if (sort === 'horas') {
      result = result.sort(
        (a, b) => (b.total_horas || 0) - (a.total_horas || 0),
      );
    }
    res.json({ data: result });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}

export async function getFornecedoresHorasCtrl(req, res) {
  try {
    const result = await getFornecedoresHoras();
    // Mapa manual de equivalências
    const manualMap = {
      // HITSS
      hitss: 'hitss',
      hitts: 'hitss',
      globalhitss: 'hitss',
      // NTTDATA
      nttdata: 'nttdata',
      ntt: 'nttdata',
      'ntt..': 'nttdata',
      // MJV
      mjv: 'mjv',
      mjvtechnologyinnovation: 'mjv',
      mjvsolucoemtecnologialtda: 'mjv',
      mjvtecnologiaeinovacao: 'mjv',
      mjvsolucoemtecnologia: 'mjv',
      mjvsolucoesemtecnologialtda: 'mjv',
      mjvsolucoesemtecnologia: 'mjv',
      'mjv technology & innovation': 'mjv',
      'mjv soluções em tecnologia ltda': 'mjv',
      // ATOS
      atos: 'atos',
      atosajustedarc1008549873pedidoemitido5500508154: 'atos',
      atosajustedarc100854987pedidoemitido5500508154: 'atos',
      'atos ajuste da rc 100854987/3 pedido emitido 5500508154': 'atos',
      // M4
      m4: 'm4',
      m4po5500509779emitidaem1106: 'm4',
      'm4 po - 5500509779 - emitida em 11/06': 'm4',
      // ENGINEERING
      engineering: 'engineering',
      engeering: 'engineering',
      enginnering: 'engineering',
      engineeringbrasil: 'engineering',
      engineeringdobrasil: 'engineering',
      engineeringdo: 'engineering',
      engeeringbrasil: 'engineering',
      engeeringdobrasil: 'engineering',
      // SITE BLINDADO
      siteblindado: 'siteblindado',
      siteblindadoltda: 'siteblindado',
    };
    const map = {};
    for (const item of result) {
      let nome = (item._id || '')
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '');
      nome = nome.replace(/[.,\-\s&]/g, '').toLowerCase();
      nome = manualMap[nome] || nome;
      // Filtros automáticos
      if (
        !nome ||
        nome === 'fornecedor' ||
        nome === '???' ||
        nome === 'ajustedarc' ||
        nome === 'pedidoemitido' ||
        nome === 'emitidaem' ||
        nome === 'multivendor'
      )
        continue;
      if (!item.total_horas || item.total_horas === 0) continue;
      if (!map[nome]) {
        map[nome] = { fornecedor: nome, total_horas: item.total_horas };
      } else {
        map[nome].total_horas += item.total_horas || 0;
      }
    }
    res.json({ data: Object.values(map) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}

export async function insertSampleToDbCtrl(req, res) {
  try {
    // Caminho do arquivo fixo (ajuste conforme necessário)
    const filePath = path.resolve(
      process.cwd(),
      'DQF - 122192 - Projeto Novas Réguas Cobrança Residencial v5.xlsx',
    );
    const parsedData = parseAndValidateFornecedores(filePath);
    const result = await insertSampleToDB(parsedData);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
