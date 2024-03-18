// user_operations.js
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('./db');

// Function to hash passwords
async function hashPassword(password) {
    const salt = await bcrypt.genSalt(10);
    return await bcrypt.hash(password, salt);
}

// Function to verify passwords
async function verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
}

// Function to register a new user
async function registerUser(username, password) {
    const hashedPassword = await hashPassword(password);
    const result = pool.query('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashedPassword]);
    return result.insertId;
}

// Function to authenticate a user and return a JWT
async function authenticateUser(username, password) {
    const result = pool.query('SELECT * FROM users WHERE username = ?', [username]);
    if (result.length === 0) {
        throw new Error('User not found');
    }
    const user = result[0];
    const isPasswordValid = await verifyPassword(password, user.password);
    if (!isPasswordValid) {
        throw new Error('Invalid password');
    }
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });
    return token;
}

// Function to verify a JWT and return the user's ID
function verifyToken(token) {
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        return decoded.userId;
    } catch (err) {
        throw new Error('Invalid token');
    }
}

// Function to get all users
async function getAllUsers() {
    const result = pool.query('SELECT * FROM users');
    return result;
}

module.exports = {
    registerUser, 
    authenticateUser, 
    verifyToken,
    getAllUsers
};