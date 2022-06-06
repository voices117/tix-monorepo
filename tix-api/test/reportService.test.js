var assert = require('assert');
var userService = require('../services/userService');
var db  = require('../models/db');
var locationService = require('../services/locationService');
var reportService = require('../services/reportService');
var providerService = require('../services/providerService');

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

    describe('createReport()', function () {
        it('should create a new report', function (done) {
            var originalReport = {
                upUsage: 0.6,
                downUsage: 0.5,
                upQuality: 0.3,
                downQuality: 0.1,
                timestamp: 1505836144,
            };
            userService.createUser("test", "test").then( user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                locationService.createInstallation(location, createdUser).then(location => {
                    reportService.postReport(originalReport, "testAs", location.get('id'), user.get('id')).then(report => {
                        assert.equal(report.get('upUsage'), originalReport.upUsage);
                        assert.equal(report.get('downUsage'), originalReport.downUsage);
                        assert.equal(report.get('upQuality'), originalReport.upQuality);
                        assert.equal(report.get('downQuality'), originalReport.downQuality);
                        assert.equal(report.get('location_id'), location.get('id'));
                        assert.equal(report.get('user_id'), createdUser.id);
                        done();
                    })
                });
            });
        });
    });

    describe('getAdminReports()', function () {
        it('should fetch a particular provider report', function (done) {
            var originalReport = {
                upUsage: 0.6,
                downUsage: 0.5,
                upQuality: 0.3,
                downQuality: 0.1,
                timestamp: 1505836144,
            };
            userService.createUser("test", "test").then( user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                providerService.createProvider("testAs").then(provider => {
                    locationService.createInstallation(location, createdUser).then(location => {
                        reportService.postReport(originalReport, "testAs", location.get('id'), user.get('id')).then(() => {
                            reportService.postReport(originalReport, "testAs2", location.get('id'), user.get('id')).then(() => {
                                reportService.getAdminReports(null, null, provider.get('id')).then(fetchedReports => {
                                    assert.equal(fetchedReports.length, 1);
                                    assert.equal(fetchedReports.models[0].get('provider_id'), provider.get('id'));
                                    done();
                                });
                            })
                        })
                    });
                });

            });
        });

        it('should fetch all reports', function (done) {
            var originalReport = {
                upUsage: 0.6,
                downUsage: 0.5,
                upQuality: 0.3,
                downQuality: 0.1,
                timestamp: 1505836144,
            };
            userService.createUser("test", "test").then( user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                providerService.createProvider("testAs").then(provider => {
                    locationService.createInstallation(location, createdUser).then(location => {
                        reportService.postReport(originalReport, "testAs", location.get('id'), user.get('id')).then(() => {
                            reportService.postReport(originalReport, "testAs2", location.get('id'), user.get('id')).then(() => {
                                reportService.getAdminReports(null, null, null).then(fetchedReports => {
                                    assert.equal(fetchedReports.length, 2);
                                    done();
                                });
                            })
                        })
                    });
                });
            });
        });
    });


    describe('getReports()', function () {
        it('should fetch a particular location report', function (done) {
            var originalReport = {
                upUsage: 0.6,
                downUsage: 0.5,
                upQuality: 0.3,
                downQuality: 0.1,
                timestamp: 1505836144,
            };
            userService.createUser("test", "test").then( user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                providerService.createProvider("testAs").then(provider => {
                    locationService.createInstallation(location, createdUser).then(location => {
                        reportService.postReport(originalReport, "testAs", location.get('id'), user.get('id')).then(() => {
                            reportService.postReport(originalReport, "testAs2", location.get('id'), user.get('id')).then(() => {
                                reportService.getReports(null, location.get('id')).then(fetchedReports => {
                                    assert.equal(fetchedReports.length, 2);
                                    done();
                                });
                            })
                        })
                    });
                });

            });
        });

        it('should fetch a location by user', function (done) {
            var originalReport = {
                upUsage: 0.6,
                downUsage: 0.5,
                upQuality: 0.3,
                downQuality: 0.1,
                timestamp: 1505836144,
            };
            userService.createUser("test", "test").then( user => {
                var createdUser = {
                    id: user.get('id')
                };
                var location = {
                    name: 'test',
                    publickey: '123456'
                }
                providerService.createProvider("testAs").then(provider => {
                    locationService.createInstallation(location, createdUser).then(location => {
                        reportService.postReport(originalReport, "testAs", location.get('id'), user.get('id')).then(() => {
                            reportService.postReport(originalReport, "testAs2", location.get('id'), user.get('id')).then(() => {
                                reportService.getReports(user.get('id')).then(fetchedReports => {
                                    assert.equal(fetchedReports.length, 2);
                                    done();
                                });
                            })
                        })
                    });
                });
            });
        });
    });
});