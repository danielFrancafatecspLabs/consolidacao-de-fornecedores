import express from 'express';
import {
  getFornecedores,
  getFornecedoresHorasCtrl,
  insertSampleToDbCtrl,
} from '../controllers/fornecedoresController.js';

const router = express.Router();

router.get('/', getFornecedores);
router.get('/horas', getFornecedoresHorasCtrl);
router.post('/insert_sample_to_db', insertSampleToDbCtrl);

export default router;
