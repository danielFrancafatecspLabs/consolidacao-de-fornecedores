import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import fornecedoresRoutes from './routes/fornecedoresRoutes.js';
import { connectDB } from './config/db.js';

dotenv.config();

// Debug: log das variáveis de ambiente
console.log('MONGODB_URI:', process.env.MONGODB_URI);
console.log('MONGODB_DB:', process.env.MONGODB_DB);

const app = express();
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ status: 'API Express rodando!' });
});

app.use('/fornecedores', fornecedoresRoutes);

const port = process.env.PORT || 3001;
connectDB().then(() => {
  app.listen(port, () => {
    console.log(`Servidor Express ouvindo na porta ${port}`);
  });
});

export default app; // Para Vercel
