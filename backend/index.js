require('dotenv').config();

const express = require('express');
const errorHandler = require('./errorHandler');
const routes = require('./user_routes'); // Import the routes
const app = express();
const port = process.env.PORT || 3000;

const cors = require('cors');

app.use(cors());

// Middleware to parse JSON bodies
app.use(express.json());

// Use the imported routes
app.use('/', routes);

// Error handling middleware
app.use(errorHandler);

// Start the server
app.listen(port, () => {
    console.log(`User management backend server is running at http://localhost:${port}`);
});