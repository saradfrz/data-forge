require('dotenv').config();
const express = require('express');
const path = require('path');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

// Serve frontend
app.use(express.static(path.join(__dirname, '../frontend')));

const pool = new Pool({
  host: process.env.POSTGRES_HOST,
  port: process.env.POSTGRES_PORT,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB
});

// API route
app.post('/api/purchase', async (req, res) => {
  const { code, description, quantity, unit_price } = req.body;
  try {
    await pool.query(
      `INSERT INTO bronze_table (code, description, quantity, unit_price) VALUES ($1,$2,$3,$4)`,
      [code, description, quantity, unit_price]
    );
    res.status(200).send('Purchase inserted!');
  } catch (err) {
    console.error(err);
    res.status(500).send('Error inserting purchase');
  }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));
