// errorHandler.js

function errorHandler(err, req, res, next) {
    console.error(err.stack);

    // Determine the status code and message based on the error type
    let statusCode = 500;
    let message = 'Something went wrong!';

    if (err.name === 'ValidationError') {
        statusCode = 400;
        message = err.message;
    } else if (err.name === 'NotFoundError') {
        statusCode = 404;
        message = 'The requested resource was not found.';
    }

    // Send the response
    res.status(statusCode).send(message);
}

module.exports = errorHandler;
