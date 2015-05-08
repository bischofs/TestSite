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

        //$scope.testDataName = 'sttuff';



    }

})();
