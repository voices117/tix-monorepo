module.exports = {
    test: {
        debug: false,
        client: 'sqlite3',
        connection: {
            filename: 'test.sqlite3'
        },
        migrations: {
            directory: './migrations'
        },
    },
    development: {
        debug: true,
        client: 'mysql',
        connection: {
            host     : 'mysql',
            user     : 'tix',
            password : 'tix',
            database : 'tix',
            charset  : 'utf8'
        },
        migrations: {
            directory: './migrations'
        },
    },
    production: {
        client: 'mysql',
        connection: {
            host     : '127.0.0.1',
            user     : 'tix',
            password : 'tix',
            database : 'tix',
            charset  : 'utf8'
        },
    }
}