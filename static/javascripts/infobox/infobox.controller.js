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

        var ListInfo = ['meta','channels','units','ranges','amb']
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

        $scope.$on('RangesUpdated',function(){

            $scope.full_ranges = infoboxService.full_ranges;
            $scope.pre_ranges = infoboxService.pre_ranges;
            $scope.test_ranges = infoboxService.test_ranges;
            $scope.post_ranges = infoboxService.post_ranges;

            $scope.l_full_ranges = "label-success";
            $scope.l_pre_ranges = "label-success";
            $scope.l_test_ranges = "label-success";        
            $scope.l_post_ranges = "label-success";                

        })

        function load_file(File) {
                    
            for (var i = 0; i < ListInfo.length; i++) {
                $scope[File+'_'+ListInfo[i]] = infoboxService[File+'_'+ListInfo[i]];
                $scope['l_'+File+'_'+ListInfo[i]] = 'label-success';
            };
        }   

        function FirstLoad() {
            $scope.cycle = 'Unknown';
            for (var i = 0; i < ListFile.length; i++) {
                for (var j = 0; j < ListInfo.length; j++) {
                    $scope[ListFile[i] + '_' + ListInfo[j]] = 'No Data';
                    $scope['l_' + ListFile[i] + '_' + ListInfo[j]] = 'label-default';
                };            
            };                  
        }     
    }
})();
