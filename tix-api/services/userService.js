var User = require('../models/User');
var nodemailer = require('nodemailer');
var uuidv4 = require('uuid/v4');
var Crypto = require('crypto');

var updateUser = (body, userId, isAdmin) => {
    return User.where('id', userId).fetch().then((user) => {
        if (!isAdmin && hashPassword(body.oldPassword, user.get('salt')) !== user.get('password')) {
            return null;
        }
        if(body.newPassword) {
            var salt = generateSalt();
            var hashedPassword = hashPassword(body.newPassword, salt);
            return user.save({password: hashedPassword, salt: salt}, {
                method: 'update',
                patch: true
            });
        } else if(body.username){
            return user.save({username: body.username}, {method: 'update', patch: true});
        } else if(body.role){
            return user.save({role: body.role}, {method: 'update', patch: true});
        }
    });
};

var createUser = (username, password) => {
    var salt = generateSalt();
    var hashedPassword = hashPassword(password, salt);
    return User.forge({
        username: username,
        password: hashedPassword,
        role: 'user',
        salt: salt,
        enabled: true
    }).save();
}

var createAdmin = (username, password) => {
    var salt = generateSalt();
    var hashedPassword = hashPassword(password, salt);
    return User.forge({
        username: username,
        password: hashedPassword,
        role: 'admin',
        salt: salt,
        enabled: true
    }).save();
}

var getUserById = (userId) => {
    return User.where('id', userId).fetch();
};

var getAllUsers = () => {
    return User.fetchAll();
}

var updatePassword = (email, recoveryCode, newPassword) => {
    return User.where('username', email).fetch().then(user => {
        if(user.get('recoveryToken') === recoveryCode){
            var salt = generateSalt();
            var hashedPassword = hashPassword(newPassword, salt);
            return user.save({password: hashedPassword, salt: salt, recoveryToken: null},{method: 'update', patch: true});
        }

    });
};

var sendUserRecoveryEmail = (email) => {
    return User.where('username', email).fetch().then(user => {
        var recoveryToken = uuidv4();
        transporter.sendMail(createEmail(user.username, recoveryToken), (error, info) => {
            if (error) {
                return console.log(error);
            }
        });
        return user.save({recoveryToken: recoveryToken},{method: 'update', patch: true});
    });
};

function createEmail(to, code) {
    return {
        from: '"TiX Service" <info@tix.innova-red.net>',
        to: to,
        subject: 'Recuperar Clave',
        text: 'Para recuperar su contraseña siga el siguiente link: http://tix.innova-red.net/recover?code=' + code + '&email=' +  to, // plain text body
        html: `<html>
                <body>
                    Para recuperar su contraseña siga el siguiente link <a href=\"http://tix.innova-red.net/recover?code=${code}&email=${to}\"
                    O ingrese a http://tix.innova-red.net/recover e ingrese el codigo ${code}
                </body>
               </html>`
    };
}

// create reusable transporter object using the default SMTP transport
let transporter = nodemailer.createTransport({
    host: 'localhost',
    port: 465,
    secure: true, // secure:true for port 465, secure:false for port 587
});

function generateSalt() {
    var salt = Crypto.randomBytes(126);
    return salt.toString('base64');
};

var hashPassword = (password, salt) => {
    var hmac =  Crypto.createHmac('sha512', salt);
    hmac.setEncoding("base64");
    hmac.write(password);
    hmac.end();
    return hmac.read();
};

module.exports = {
    sendUserRecoveryEmail: sendUserRecoveryEmail,
    updatePassword: updatePassword,
    getAllUsers: getAllUsers,
    getUserById: getUserById,
    createUser: createUser,
    createAdmin: createAdmin,
    updateUser: updateUser,
    hashPassword: hashPassword,
    generateSalt: generateSalt,
};