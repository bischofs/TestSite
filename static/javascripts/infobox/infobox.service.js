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

        var ListInfo = ['meta','channels','units','ranges','amb']
        var service = {};

        service.updateFull = function() {
            updateFile('full');         
            $rootScope.$broadcast("FullUploaded");
        }

        service.updatePre = function() {
            updateFile('pre');  
            $rootScope.$broadcast("PreUploaded");
        }        

        service.updateTest = function(CycleAttr){

            service.cycle  = CycleAttr['Cycle'];
            service.CycleType = CycleAttr['CycleType'];
            updateFile('test');

            $rootScope.$broadcast("TestUploaded");
        }

        service.updatePost = function() {
            updateFile('post');          
            $rootScope.$broadcast("PostUploaded");
        }

        service.finishUpload = function() {
            service.amb = 'OK';    
            service.ranges = 'OK';   
            service.timestamp = 'OK';    
            $rootScope.$broadcast("FinishedUpload");
        }

        service.resetAll =function(){
            $rootScope.$broadcast("ResetAll");
        }

        return service

        function updateFile (File) {                
            for (var i = 0; i < ListInfo.length; i++) {
                service[File+'_'+ListInfo[i]] = 'OK';
            };
        }        
    }
})();
