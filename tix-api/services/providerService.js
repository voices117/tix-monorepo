var Provider = require('../models/Provider');

var getProvider = (providerId) => {
    return Provider.where('id', providerId).fetchAll();
};

var getProviders = () => {
    return Provider.fetchAll();
};

var createProvider = (as) => {
    return Provider.forge({
        name: as
    }).save();
}

var getProviderByAs = (as) => {
    return Provider.where('name', as).fetch();
}

module.exports = {
    getProvider: getProvider,
    getProviders: getProviders,
    createProvider: createProvider,
    getProviderByAs: getProviderByAs,
};