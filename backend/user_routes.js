// user_routes.js
const express = require('express');
const router = express.Router();
const { registerUser, authenticateUser, verifyToken, getAllUsers } = require('./user_operations');

// Route for getting all users
router.get('/users', async (req, res, next) => {
    try {
        const users = await getAllUsers();
        res.send(users);
    } catch (err) {
        next(err);
    }
});

// Route for user registration
router.post('/users/register', async (req, res, next) => {
    try {
        const { username, password } = req.body;
        const userId = await registerUser(username, password);
        res.status(201).send({ userId });
    } catch (err) {
        next(err);
    }
});

// Route for user login
router.post('/users/login', async (req, res, next) => {
    try {
        const { username, password } = req.body;
        const token = await authenticateUser(username, password);
        res.send({ token });
    } catch (err) {
        next(err);
    }
});

// Middleware to verify JWT
function authenticateJWT(req, res, next) {
    const token = req.headers.authorization;
    if (!token) {
        return res.status(401).send({ message: 'No token provided' });
    }
    try {
        const userId = verifyToken(token);
        req.userId = userId;
        next();
    } catch (err) {
        next(err);
    }
}

// Protected route example
router.get('/users/protected', authenticateJWT, (req, res) => {
    res.send({ message: 'You are authenticated!' });
});

module.exports = router;