/**
 * NavbarController
 * @namespace TestSite.import.controllers
 */
(function() {
    'use strict';

    angular
        .module('TestSite.import.controllers')
        .controller('ImportController', ImportController);

    ImportController.$inject = ['$scope', 'FileUploader', 'toastr', 'infoboxService'];

    /*
     * @namespace UploadController
     */
    function ImportController($scope, FileUploader, toastr, infoboxService) {

        $scope.uploader = new FileUploader();
        $scope.uploader.url = 'api/v1/data/import/'
        $scope.uploader.method = 'POST'
        $scope.filetype = '';


        //$scope.uploader.formData.push({cycle: 'FTP'});
        $scope.uploader.formData.push({
            bench: '1'
        });
        $scope.uploader.onSuccessItem = onSuccessItem;
        $scope.uploader.onErrorItem = onErrorItem;
        $scope.uploader.onBeforeUploadItem = onBeforeUploadItem;

        function onBeforeUploadItem(item) {
            if ($scope.filetype == "pre") {
                $scope.uploader.formData.push({
                    ftype: "pre"
                });
            } else if ($scope.filetype == "post") {
                $scope.uploader.formData.push({
                    ftype: "post"
                });
            } else if ($scope.filetype == "full") {
                $scope.uploader.formData.push({
                    ftype: "full"
                });
            } else if ($scope.filetype == "test") {
                $scope.uploader.formData.push({
                    ftype: "test"
                });
            }
            item.formData = $scope.uploader.formData
        }


        function onSuccessItem(item, response, status, headers) {

            toastr.success('File Uploaded', 'Success');
            $scope.uploadSuccess = true;


            if (response.indexOf("Meta-Data missing") > -1) {
                $scope.metaDataPresent = false;
            } else {
                $scope.metaDataPresent = true;
            }

            if (response.indexOf("units are not") > -1 || response.indexOf("Cannot find") > -1) {
                $scope.requiredChannels = false;
            } else {
                $scope.requiredChannels = true;
            }

            if (response.indexOf("out of range") > -1) {
                $scope.ambientConditions = false;
            } else {
                $scope.ambientConditions = true;
            }


            infoboxService.addItem("true");


            var jsonObj = JSON.parse(response);

            if ($scope.filetype == "test") {
                $scope.powerI = jsonObj.regression.Power.intercept
                $scope.powerr = jsonObj.regression.Power.rsquared
                $scope.powers = jsonObj.regression.Power.slope
                $scope.powerse = jsonObj.regression.Power.standard_error

                $scope.speedI = jsonObj.regression.Speed.intercept
                $scope.speedr = jsonObj.regression.Speed.rsquared
                $scope.speeds = jsonObj.regression.Speed.slope
                $scope.speedse = jsonObj.regression.Speed.standard_error

                $scope.torqI = jsonObj.regression.Torque.intercept
                $scope.torqr = jsonObj.regression.Torque.rsquared
                $scope.torqs = jsonObj.regression.Torque.slope
                $scope.torqse = jsonObj.regression.Torque.standard_error
            }
        }

        function onErrorItem(item, response, status, headers) {
            toastr.error(response.message, 'Error');
            $scope.uploadSuccess = false;

        }


    }

})();
