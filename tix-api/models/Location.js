var db = require('./db');
var Bookshelf = require('bookshelf')(db.knex);
var Provider = require('./Provider');
var Measure = require('./Measure');
Bookshelf.plugin('registry');

module.exports = Bookshelf.Model.extend({
    tableName: 'location',
    hasTimestamps: true,
    measures: function() {
        return this.hasMany(Measure);
    },
    providers: function() {
        return this.belongsToMany(Provider);
    }
});