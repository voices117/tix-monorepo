var assert = require('assert');
var userService = require('../services/userService');
var db  = require('../models/db');


describe('User Service', function() {

    beforeEach(function(done) {
        db.migrate.rollback()
            .then(function() {
                db.migrate.latest()
                    .then(function() {
                        done();
                    });
            });
    });

    afterEach(function(done) {
        db.migrate.rollback()
            .then(function() {
                done();
            });
    });

    describe('createUser()', function() {
        it('should return the new created user', function(done) {
            userService.createUser("test", "test").then( user => {
                assert.equal(user.get('username'), "test");
                var salt = user.get('salt');
                assert.equal(user.get('password'), userService.hashPassword("test", salt));
                assert.equal(user.get('enabled'), true);
                done();
            });
        });
    });

    describe('getUserById()', function() {
        it('should return the user requested', function(done) {
            userService.createUser("test", "test").then( user => {
                userService.getUserById(user.get('id')).then((fetchedUser) => {
                    assert.equal(user.get('username'), fetchedUser.get('username'));
                    done();
                })
            });
        });
    });

    describe('updateUser()', function() {
        it('should update the user password', function(done) {
            userService.createUser("test", "test").then( user => {
                var body = {
                    oldPassword: "test",
                    newPassword: "test2"

                };
                userService.updateUser(body, user.get('id')).then((editedUser) => {
                    assert.equal(userService.hashPassword("test2", editedUser.get("salt")), editedUser.get('password'));
                    done();
                })
            });
        });

        it('should update the user username', function(done) {
            userService.createUser("test", "test").then( user => {
                var body = {
                    oldPassword: "test",
                    username: "test2"

                };
                userService.updateUser(body, user.get('id')).then((editedUser) => {
                    assert.equal("test2", editedUser.get('username'));
                    done();
                })
            });
        });
    });
});