var assert = require('assert');
var providerService = require('../services/providerService');
var db  = require('../models/db');

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

    describe('createProvider()', function () {
        it('should return the new created provider', function (done) {
            providerService.createProvider("testAs").then(provider => {
                assert.equal(provider.get('name'), "testAs");
                done();
            });
        });
    });

    describe('getProviders()', function () {
        it('should return all the created providers', function (done) {
            providerService.createProvider("testAs").then(provider => {
                providerService.getProviders().then(providers => {
                    assert.equal(providers.length, 1);
                    assert.equal(providers.models[0].get('name'), 'testAs');
                    done();
                });
            });
        });
    });

    describe('getProvider()', function () {
        it('should return the selected provider', function (done) {
            providerService.createProvider("testAs").then(provider => {
                providerService.getProvider(provider.get('id')).then(fetchedProvider => {
                    assert.equal(fetchedProvider.length, 1);
                    assert.equal(fetchedProvider.models[0].get('name'), "testAs");
                    done();
                });
            });
        });
    });

    describe('getProviderByAs()', function () {
        it('should return the selected provider', function (done) {
            providerService.createProvider("testAs").then(provider => {
                providerService.getProviderByAs('testAs').then(fetchedProvider => {
                    assert.equal(fetchedProvider.get('name'), "testAs");
                    done();
                });
            });
        });
    });
});