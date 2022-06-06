
exports.up = function(knex, Promise) {
	return Promise.all([
		knex.schema.createTable('user', function(table) {
			table.increments('id').primary();
			table.string('username').unique();
			table.string('salt');
			table.string('password');
			table.boolean('enabled');
			table.string('role');
			table.string('recoveryToken');
			table.datetime('created_at');
            table.datetime('updated_at');
		}).createTable('provider', function(table) {
            table.increments('id').primary();
            table.string('name');
            table.datetime('created_at');
            table.datetime('updated_at');
        }).createTable('location', function(table) {
			table.increments('id').primary();
			table.string('name');
			table.string('publickey', 500);
            table.boolean('enabled');
			table.integer('user_id').unsigned();
			table.foreign('user_id').references('user.id');
            table.datetime('created_at');
            table.datetime('updated_at');
		}).createTable('measure', function(table) {
			table.increments('id').primary();
			table.double('usagePercentage');
			table.double('upUsage');
			table.double('downUsage');
			table.double('upQuality');
			table.double('downQuality');
			table.datetime('timestamp');
            table.integer('location_id').unsigned();
            table.integer('provider_id').unsigned();
            table.integer('user_id').unsigned();
			table.foreign('location_id').references('id').inTable('location');
			table.foreign('provider_id').references('id').inTable('provider');
			table.foreign('user_id').references('id').inTable('user');
            table.datetime('created_at');
            table.datetime('updated_at');
		}).createTable('location_provider', function(table) {
            table.increments('id').primary();
            table.integer('location_id').unsigned();
            table.integer('provider_id').unsigned();
		})
	])
};

exports.down = function(knex, Promise) {
	return Promise.all([
    	knex.schema.dropTable('measure')
			.dropTable('provider')
    		.dropTable('location')
    		.dropTable('user')
			.dropTable('location_provider')
	])
};
