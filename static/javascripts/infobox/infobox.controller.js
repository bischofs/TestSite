(function() {
    'use strict';

    angular
        .module('TestSite.infobox.controllers')
        .controller('InfoboxController', InfoboxController);

    InfoboxController.$inject = ['$scope', 'FileUploader', 'toastr', 'infoboxService'];

    /**
     * @namespace UploadController
     */
    function InfoboxController($scope, FileUploader, toastr, infoboxService) {


        $scope.myList = infoboxService.getList();
        $scope.testDataName = $scope.myList[2];

        $scope.cycle = 'None'

        $scope.pre_meta = 'None';
        $scope.pre_units = 'None';
        $scope.pre_ranges = 'None';
        $scope.pre_amb = 'None';
        $scope.pre_channels = 'None';

        $scope.full_meta = 'None';
        $scope.full_units = 'None';
        $scope.full_ranges = 'None';
        $scope.full_amb = 'None';
        $scope.full_channels = 'None';

        $scope.post_meta = 'None';
        $scope.post_units = 'None';
        $scope.post_ranges = 'None';
        $scope.post_amb = 'None';
        $scope.post_channels = 'None';

        $scope.test_meta = 'None';
        $scope.test_units = 'None';
        $scope.test_ranges = 'None';
        $scope.test_amb = 'None';
        $scope.test_channels = 'None';

        $scope.$on('FullUploaded',function(){
            $scope.full_meta = infoboxService.full_meta;
            $scope.full_units = infoboxService.full_units;
            $scope.full_ranges = infoboxService.full_ranges,
            $scope.full_amb = infoboxService.full_amb;
            $scope.full_channels = infoboxService.full_channels;        

        })        

        $scope.$on('PreUploaded',function(){
            $scope.pre_meta = infoboxService.pre_meta;
            $scope.pre_units = infoboxService.pre_units;
            $scope.pre_ranges = infoboxService.pre_ranges,
            $scope.pre_amb = infoboxService.pre_amb;
            $scope.pre_channels = infoboxService.pre_channels;        

        })        

        $scope.$on('TestUploaded',function(){

            $scope.cycle = infoboxService.cycle;

            $scope.test_meta = infoboxService.test_meta;
            $scope.test_units = infoboxService.test_units;
            $scope.test_ranges = infoboxService.test_ranges,
            $scope.test_amb = infoboxService.test_amb;
            $scope.test_channels = infoboxService.test_channels;

            
        });

        $scope.$on('PostUploaded',function(){
            $scope.post_meta = infoboxService.post_meta;
            $scope.post_units = infoboxService.post_units;
            $scope.post_ranges = infoboxService.post_ranges,
            $scope.post_amb = infoboxService.post_amb;
            $scope.post_channels = infoboxService.post_channels;           

        })


        //$scope.testDataName = 'sttuff';



    }

})();
