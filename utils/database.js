// utils/database.js

const mysql = require('mysql2');

const db = mysql.createConnection({
    host: 'localhost',
    user: 'shivam',
    password: 'shiva@123',
    database: 'practice',
   
});

db.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL database');
        throw err;
    }
    console.log('Connected to MySQL database');
});

module.exports = db;
