var Location = require('../models/Location');

var deleteInstallation = (installationId, userId) => {
    return Location.where('id', installationId).where('user_id', userId).where('enabled', true).fetch()
        .then((installation) => installation.save({enabled: false},{method: 'update', patch: true}));
};

var updateInstallation = (installationId, userId, name) => {
    return Location.where('id', installationId).where('user_id', userId).where('enabled', true).fetch()
        .then(installation => installation.save({name: name},{method: 'update', patch: true}));
};

var getInstallation = (installationId, userId) => {
    return Location.where('id', installationId).where('user_id', userId).where('enabled', true).fetch({withRelated: ['providers']})
};

var getInstallations = (userId) => {
    return Location.where('user_id', userId).where('enabled', true).fetchAll({withRelated: ['providers']})
};

var getInstallationByUserId = (userId) => {
    return Location.where('user_id', userId).fetchAll();
}

var createInstallation = (location, user) => {
    return Location.forge({
        name: location.name,
        publickey: location.publickey,
        user_id: user.id,
        enabled: true
    }).save();
}

module.exports = {
    deleteInstallation: deleteInstallation,
    updateInstallation: updateInstallation,
    getInstallation: getInstallation,
    getInstallations: getInstallations,
    createInstallation: createInstallation,
    getInstallationByUserId: getInstallationByUserId,
};