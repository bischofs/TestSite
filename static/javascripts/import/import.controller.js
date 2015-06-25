/**
 * NavbarController
 * @namespace TestSite.import.controllers
 */
 (function() {
    'use strict';

    angular
    .module('TestSite.import.controllers')
    .controller('ImportController', ImportController);

    ImportController.$inject = ['$scope', 'FileUploader', 'toastr', 'infoboxService', '$http'];

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

        $scope.Regression = function() {

            // Fill in Regression Data
            $.get("api/v1/data/import/",{choice:document.getElementById("sel1").value}) 
                .done(function(response){
                    var jsonObj = JSON.parse(response);
                    var List_channel = ['Power','Speed','Torque'];
                    var List_regType = ['intercept','rsquared','slope','standard_error'];
                    var result = "";

                    // List_reg has all Ids of panels of the Regression
                    var List_reg = [['powerI','powerr','powers','powerse'],['speedI','speedr','speeds','speedse'],['torqueI','torquer','torques','torquese']]               

                    for (var j = 0; j < List_channel.length; j++) {
                            var channel = List_channel[j];
                            var List_label = List_reg[j];

                            for (var i = 0; i < List_regType.length; i++) {

                                    if (jsonObj.Regression_bool[channel][List_regType[i]]) {
                                            result = "label label-success";
                                    }             
                                    else {
                                            result = "label label-danger";                            
                                    }
                                    document.getElementById(List_label[i]).className = result; 
                                    document.getElementById(List_label[i]).innerHTML = jsonObj.Regression[channel][List_regType[i]].toFixed(2);
                            };
                    };
                })
                .error(function(response) {
                    toastr.error(response.message, 'Data is not available!');
                });
        }

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
        }


        function onErrorItem(item, response, status, headers) {

            toastr.error(response.message, 'Error');
            $scope.uploadSuccess = false;

        }

    }

})()
