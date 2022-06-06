var db  = require('./db');
var Bookshelf = require('bookshelf')(db);
var Location = require('./Location');
Bookshelf.plugin('registry');

module.exports = Bookshelf.Model.extend({
    tableName: 'user',
    hasTimestamps: true,
    locations: function(){
        return this.hasMany(Location)
    },
});
