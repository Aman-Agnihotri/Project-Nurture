// models/user.js

const db = require('../utils/database');

class User {
    constructor(username, email, password) {
        this.username = username;
        this.email = email;
        this.password = password;
    }

    static createUser(username, email, password) {
        const hashedPassword = bcrypt.hashSync(password, 10);
        const user = new User(username, email, hashedPassword);
        return new Promise((resolve, reject) => {
            db.query('INSERT INTO users SET ?', user, (err, result) => {
                if (err) {
                    console.error('Error creating user:', err);
                    reject(err);
                    return;
                }
                console.log('User created:', result);
                resolve(result);
            });
        });
    }

    static getUserByEmail(email) {
        return new Promise((resolve, reject) => {
            db.query('SELECT * FROM users WHERE email = ?', [email], (err, result) => {
                if (err) {
                    console.error('Error fetching user by email:', err);
                    reject(err);
                    return;
                }
                resolve(result[0]); // Assuming there's only one user with the given email
            });
        });
    }
}

module.exports = User;
