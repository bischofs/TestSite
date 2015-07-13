/**
 * infobox metadata service
 * @namespace TestSite.infobox.services
 */
(function() {
    'use strict';

    angular
        .module('TestSite.infobox.services')
        .service('infoboxService', infoboxService);

    function infoboxService($rootScope) {

        var myList = ["some", "data"];
        var service = {};

        service.updateFull = function() {
            service.full_meta = 'True';
            service.full_units = 'True';
            service.full_ranges = 'True';
            service.full_amb = 'True';
            service.full_channels = 'True';            
            $rootScope.$broadcast("FullUploaded");
        }

        service.updatePre = function() {
            service.pre_meta = 'True';
            service.pre_units = 'True';
            service.pre_ranges = 'True';
            service.pre_amb = 'True';
            service.pre_channels = 'True';
            $rootScope.$broadcast("PreUploaded");
        }        

        service.updateTest = function(cycle){

            service.cycle  = cycle;

            service.test_meta = 'True';
            service.test_units = 'True';
            service.test_ranges = 'True';
            service.test_amb = 'True';
            service.test_channels = 'True';

            $rootScope.$broadcast("TestUploaded");
        }

        service.updatePost = function() {
            service.post_meta = 'True';
            service.post_units = 'True';
            service.post_ranges = 'True';
            service.post_amb = 'True';
            service.post_channels = 'True';            
            $rootScope.$broadcast("PostUploaded");
        }


        service.getList= function() {
            return myList;
        }

        service.addItem = function(newObj) {
            myList.push(newObj);
        }

        return service



    }

})();
