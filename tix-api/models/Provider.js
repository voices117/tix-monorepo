var db = require('./db');
var Bookshelf = require('bookshelf')(db.knex);
var Location = require('./Location');
var Measure = require('./Measure');
Bookshelf.plugin('registry');

module.exports = Bookshelf.Model.extend({
    tableName: 'provider',
    hasTimestamps: true,
    measures: function() {
        return this.hasMany(Measure);
    },
    locations: function() {
        return this.belongsToMany(Location);
    }
});