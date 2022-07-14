var config = require('./knexfile.js');
var env = process.env.NODE_ENV ? process.env.NODE_ENV : 'development';
var knex = require('knex')(config[env]);

module.exports = {
    'knex': knex,
    'migrate': function() {
        return knex.migrate.latest([config])
    }
};