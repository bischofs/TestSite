(function() {
    'use strict';

    angular
        .module('TestSite.infobox.controllers')
        .controller('InfoboxController', InfoboxController);

    InfoboxController.$inject = ['$scope', 'FileUploader', 'toastr', 'infoboxService','$http'];

    /**
     * @namespace UploadController
     */
    function InfoboxController($scope, FileUploader, toastr, infoboxService, $http) {

        var ListInfo = ['meta','channels','units']
        var ListFile = ['full','pre','test','post']

        FirstLoad();

        $scope.Reset = function() {

            $.get("/1065/api/v1/data/meta/")
            .done(function(response){
                infoboxService.resetAll();               
                toastr.success(response.message);                   
            })            
            
        } 

        $scope.$on('ResetAll',function(){
            FirstLoad();          
        })      

        $scope.$on('FullUploaded',function(){
            load_file('full')
        })        

        $scope.$on('PreUploaded',function(){
            load_file('pre')
        })        

        $scope.$on('TestUploaded',function(){
            $scope.cycle = infoboxService.cycle;
            load_file('test')           
        });

        $scope.$on('PostUploaded',function(){                   
            load_file('post')
        })

        $scope.$on('FinishedUpload',function(){

            // Text for General Tests
            $scope.ranges = infoboxService.ranges;
            $scope.amb = infoboxService.amb;
            $scope.timestamp = infoboxService.timestamp;

            // Success Labels for General Tests
            $scope.l_ranges = "label-success";
            $scope.l_amb = "label-success";
            $scope.l_timestamp = "label-success";        

        })

        function load_file(File) {
                    
            for (var i = 0; i < ListInfo.length; i++) {
                $scope[File+'_'+ListInfo[i]] = infoboxService[File+'_'+ListInfo[i]];
                $scope['l_'+File+'_'+ListInfo[i]] = 'label-success';
            };
        }   

        function FirstLoad() {

            $scope.cycle = 'Unknown';

            // Text for General Tests
            $scope.ranges = 'NA';
            $scope.amb = 'NA';
            $scope.timestamp = 'NA';

            // Default Labels for General Tests
            $scope.l_amb = 'label-default';
            $scope.l_ranges = 'label-default';
            $scope.l_timestamp = 'label-default';

            // Text and Labels for File-Checks            
            for (var i = 0; i < ListFile.length; i++) {
                for (var j = 0; j < ListInfo.length; j++) {
                    $scope[ListFile[i] + '_' + ListInfo[j]] = 'NA';
                    $scope['l_' + ListFile[i] + '_' + ListInfo[j]] = 'label-default';
                };            
            };                  
        }     
    }
})();
