// user_routes.js

/**
 * Express router for handling user routes.
 * @module user_routes
 */

const express = require('express');
const router = express.Router();
const { 
    registerUser, 
    authenticateUser, 
    verifyToken, 
    getAllUsers, 
    deleteUser,
    UserNotFoundError } = require('./user_operations');

/**
 * Route for getting all users.
 * @name GET /users
 * @function
 * @async
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware function.
 */
router.get('/users', async (req, res, next) => {
    try {
        const users = await getAllUsers();
        res.json(users);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to retrieve users!', error: error.message });
    }
});

router.delete('/users/:id', async (req, res, next) => {
    try {
        const id = parseInt(req.params.id);
        const affectedRows = await deleteUser(id);
        if (affectedRows === 0) {
            throw new UserNotFoundError(`User with ID ${id} not found!`);
        }
        res.json({ message: 'User deleted successfully!' });
    } catch (error) {
        if (error instanceof UserNotFoundError) {
            res.status(404).json({ message: error.message });
        } else {
            console.error(error);
            res.status(500).json({ message: 'Failed to delete user!', error: error.message });
        }
    }
});

/**
 * Route for user registration.
 * @name POST /users/register
 * @function
 * @async
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware function.
 */
router.post('/users/register', async (req, res, next) => {
    try {
        const { username, email, password } = req.body;
        const userId = await registerUser(username, email, password);
        res.status(201).send({ userId });
        console.log('User registered!');
    } catch (err) {
        console.error(err);
        res.status(500).json({ message: 'Internal server error!', error: err.message });
    }
});

/**
 * Route for user login.
 * @name POST /users/login
 * @function
 * @async
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware function.
 */
router.post('/users/login', async (req, res, next) => {
    try {
        const { email, password } = req.body;
        const token = await authenticateUser(email, password);
        res.send({ token });
        console.log('User logged in!');
        console.log('Token:', token);
    } catch (err) {
        next(err);
    }
});

/**
 * Middleware to verify JWT.
 * @name authenticateJWT
 * @function
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware function.
 */
function authenticateJWT(req, res, next) {
    const authHeader = req.headers.authorization;
    if (!authHeader) {
        return res.status(401).send({ message: 'No token provided!' });
    }
    const token = authHeader.split(' ')[1]; // Extract the token part
    try {
        const userId = verifyToken(token);
        req.userId = userId;
        next();
    } catch (err) {
        next(err);
    }
}

/**
 * Protected route.
 * @name GET /users/protected
 * @function
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 */
router.get('/users/protected', authenticateJWT, (req, res) => {
    res.send({ message: 'You are authenticated!' });
});

/**
 * Error handling middleware.
 * @name errorMiddleware
 * @function
 * @param {Object} err - Error object.
 * @param {Object} req - Express request object.
 * @param {Object} res - Express response object.
 * @param {Function} next - Express next middleware function.
 */
router.use((err, req, res, next) => {
    console.error(err);
    res.status(500).json({ message: 'Internal server error!', error: err.message });
});

module.exports = router;