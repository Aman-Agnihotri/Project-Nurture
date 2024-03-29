// user_operations.js
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('./db');

class UserNotFoundError extends Error {
    constructor(message) {
        super(message);
        this.name = 'UserNotFoundError';
    }
}

class InvalidPasswordError extends Error {
    constructor(message) {
        super(message);
        this.name = 'InvalidPasswordError';
    }
}

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
/**
 * Registers a new user by inserting the provided username and hashed password into the database.
 * @param {string} username - The username of the user to register.
 * @param {string} email - The email of the user to register.
 * @param {string} password - The password of the user to register.
 * @returns {Promise<number>} - A Promise that resolves to the ID of the newly registered user.
 * @throws {Error} - If an error occurs while inserting the user into the database.
 */
async function registerUser(username, email, password) {
    return new Promise((resolve, reject) => {
        hashPassword(password).then(hashedPassword => {
            pool.query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', [username, email, hashedPassword], (error, results) => {
                if (error) {
                    reject(error);
                } else {
                    resolve(results.insertId);
                }
            });
        }).catch(error => reject(error));
    });
}

// Function to authenticate a user and return a JWT
/**
 * Authenticates a user by checking the provided username and password against the database.
 * If the user is found and the password is valid, a JSON Web Token (JWT) is generated and returned.
 * @param {string} username - The username of the user to authenticate.
 * @param {string} password - The password of the user to authenticate.
 * @returns {Promise<string>} - A Promise that resolves to a JWT if the authentication is successful.
 * @throws {UserNotFoundError} - If the user with the provided username is not found in the database.
 * @throws {InvalidPasswordError} - If the provided password is invalid.
 */

async function authenticateUser(username, password) {
    return new Promise((resolve, reject) => {
        pool.query('SELECT * FROM users WHERE username = ?', [username], async (error, results) => {
            if (error) {
                reject(error);
            } else if (results.length === 0) {
                reject(new UserNotFoundError('User not found'));
            } else {
                const user = results[0];
                const isPasswordValid = await verifyPassword(password, user.password);
                if (!isPasswordValid) {
                    reject(new InvalidPasswordError('Invalid password'));
                } else {
                    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '12h' });
                    resolve(token);
                }
            }
        });
    });
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
    return new Promise((resolve, reject) => {
        const query = 'SELECT * FROM users';
        pool.query(query, (error, results) => {
            if (error) {
                reject(error);
            } else {
                resolve(results);
            }
        });
    });
}

module.exports = {
    registerUser,
    authenticateUser,
    verifyToken,
    getAllUsers,
    UserNotFoundError,
    InvalidPasswordError
};