var userContract = (user) => {
    return {
        username: user.get('username'),
        role: user.get('role'),
        id: user.id,
        enabled: user.get('enabled')
    }
}

var measureContract = (measure) => {
    return {
        upUsage: measure.get('upUsage'),
        downUsage: measure.get('downUsage'),
        upQuality: measure.get('upQuality'),
        downQuality: measure.get('downQuality'),
        timestamp: measure.get('timestamp'),
        location_id: measure.get('location_id'),
        provider_id: measure.get('provider_id'),
        user_id: measure.get('user_id')
    }
}

var installationContract = (installation) => {
    return {
        id: installation.id,
        name: installation.get('name'),
        publickey: installation.get('publickey'),
        providers: installation.related('providers').map(provider => providerContract(provider))
    }
}

var providerContract = (provider) => {
    return {
        id: provider.id,
        name: provider.get('name'),
    }
}

module.exports = {
    userContract: userContract,
    measureContract: measureContract,
    installationContract: installationContract,
    providerContract: providerContract,
};