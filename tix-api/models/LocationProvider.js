var db  = require('./db');
var Bookshelf = require('bookshelf')(db);
Bookshelf.plugin('registry');

module.exports = Bookshelf.Model.extend({
    tableName: 'location_provider',
    hasTimestamps: false
});
