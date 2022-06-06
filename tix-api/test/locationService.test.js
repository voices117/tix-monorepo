var assert = require('assert');
var userService = require('../services/userService');
var db  = require('../models/db');
var locationService = require('../services/locationService');

describe('Location Service', function() {

    beforeEach(function (done) {
        db.migrate.rollback()
            .then(function () {
                db.migrate.latest()
                    .then(function () {
                        done();
                    });
            });
    });

    afterEach(function (done) {
        db.migrate.rollback()
            .then(function () {
                done();
            });
    });

    describe('createInstallation()', function() {
        it('should return the new created location', function(done) {
            userService.createUser("test", "test").then( user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    assert.equal(location.get('name'), "test");
                    assert.equal(location.get('publickey'), "123456");
                    assert.equal(location.get('enabled'), true);
                    done();
                });
            });
        });
    });

    describe('getInstallationByUserId()', function() {
        it('should return the installations based on userId', function (done) {
            userService.createUser("test", "test").then(user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    locationService.getInstallationByUserId(createdUser.id).then(fetchedLocations => {
                        assert.equal(fetchedLocations.length, 1);
                        assert.equal(fetchedLocations.models[0].get('name'), "test");
                        assert.equal(fetchedLocations.models[0].get('publickey'), "123456");
                        assert.equal(fetchedLocations.models[0].get('enabled'), true);
                        done();
                    });
                });
            });
        });
    });

    describe('getInstallations()', function() {
        it('should return the user installations', function (done) {
            userService.createUser("test", "test").then(user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    locationService.getInstallations(createdUser.id).then(fetchedLocations => {
                        assert.equal(fetchedLocations.length, 1);
                        assert.equal(fetchedLocations.models[0].get('name'), "test");
                        assert.equal(fetchedLocations.models[0].get('publickey'), "123456");
                        assert.equal(fetchedLocations.models[0].get('enabled'), true);
                        done();
                    });
                });
            });
        });
    });

    describe('getInstallation()', function() {
        it('should return the user installation based on the id', function (done) {
            userService.createUser("test", "test").then(user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    locationService.getInstallation(location.get('id'), createdUser.id).then(fetchedLocation => {
                        assert.equal(fetchedLocation.get('name'), "test");
                        assert.equal(fetchedLocation.get('publickey'), "123456");
                        assert.equal(fetchedLocation.get('enabled'), true);
                        done();
                    });
                });
            });
        });
    });

    describe('updateInstallation()', function() {
        it('should update the selected installation', function (done) {
            userService.createUser("test", "test").then(user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    locationService.updateInstallation(location.get('id'), createdUser.id, "test2").then(editedLocation => {
                        assert.equal(editedLocation.get('name'), "test2");
                        done();
                    });
                });
            });
        });
    });

    describe('updateInstallation()', function() {
        it('should delete the selected installation', function (done) {
            userService.createUser("test", "test").then(user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    locationService.deleteInstallation(location.get('id'), createdUser.id).then(editedLocation => {
                        assert.equal(editedLocation.get('enabled'), false);
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               done();
                    });
                });
            });
        });
    });
});