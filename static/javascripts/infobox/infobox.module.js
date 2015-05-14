(function() {
    'use strict';

    angular.module('TestSite.infobox', [
            'TestSite.infobox.controllers',
            'TestSite.infobox.services'
        ]);

    angular.module('TestSite.infobox.services', []);
    angular.module('TestSite.infobox.controllers', ['angularFileUpload', 'ngAnimate', 'toastr']);



})();
