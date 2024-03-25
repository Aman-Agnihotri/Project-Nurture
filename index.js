// index.js

const express = require('express');
const bodyParser = require('body-parser');
const authRoutes = require('./routes/authRoutes');
const PORT = process.env.PORT || 3000;

const app = express();

// Middleware
app.use(bodyParser.json());

// Routes
app.use('/auth', authRoutes);

// Start server
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
