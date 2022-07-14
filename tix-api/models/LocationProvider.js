var db = require('./db');
var Bookshelf = require('bookshelf')(db.knex);
Bookshelf.plugin('registry');

module.exports = Bookshelf.Model.extend({
    tableName: 'location_provider',
    hasTimestamps: false
});