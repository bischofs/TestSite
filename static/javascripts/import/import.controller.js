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
        $scope.uploader.url = '/1065/api/v1/data/import/'
        $scope.uploader.method = 'POST'
        $scope.filetype = '';
        //$scope.uploader.formData.push({cycle: 'FTP'});
        $scope.uploader.formData.push({
            bench: '1'
        });
        $scope.uploader.onSuccessItem = onSuccessItem;
        $scope.uploader.onErrorItem = onErrorItem;
        $scope.uploader.onBeforeUploadItem = onBeforeUploadItem;

        // Load default Values for Regression Panel
        var List_reg = ['powerI','powerr','powers','powerse','speedI','speedr','speeds','speedse','torqueI','torquer','torques','torquese']            
        for (var i = 0; i < List_reg.length; i++) {
            $scope[List_reg[i]] = 'Unknown'
            $scope['label_' + List_reg[i]] = 'label-default'
        };

        $scope.Regression = function() {

            // Fill in Regression Data
            $.get("/1065/api/v1/data/import/",{choice:document.getElementById("sel1").value}) 
                .done(function(response){
                    var jsonObj = JSON.parse(response);
                    var List_channel = ['Power','Speed','Torque'];
                    var List_regType = ['Intercept','Rsquared','Slope','Standard Error'];
                    var result = "";
                    var List_reg = [['powerI','powerr','powers','powerse'],['speedI','speedr','speeds','speedse'],['torqueI','torquer','torques','torquese']]
                    
                    for (var i = 0; i < List_channel.length; i++) {
                            var channel = List_channel[i];
                            var List_label = List_reg[i];

                            for (var j = 0; j < List_regType.length; j++) {

                                    if (jsonObj.Regression_bool[channel][List_regType[j]]) {
                                            result = "label-success";
                                    }             
                                    else {
                                            result = "label-danger";                            
                                    }
                                    $scope['label_' + List_label[j]] = result;
                                    $scope[List_label[j]] = jsonObj.Regression[channel][List_regType[j]].toFixed(2);
                            };
                    };
                    $scope.$apply();
                })

                .error(function(response) {
                    toastr.error(response.message, 'Data is not available');
                });
        }

        function onBeforeUploadItem(item) {

            if ($scope.filetype == "full") {
                $scope.uploader.formData.push({
                    ftype: "full"
                });
            } 
            else if ($scope.filetype == "pre") {
                $scope.uploader.formData.push({
                    ftype: "pre"
                });
            } else if ($scope.filetype == "test") {
                $scope.uploader.formData.push({
                    ftype: "test"
                });
            } else if ($scope.filetype == "post") {
                $scope.uploader.formData.push({
                    ftype: "post"
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

            var jsonObj = JSON.parse(response);
            if (jsonObj.File == 'FULL') {
                infoboxService.updateFull();
            } else if(jsonObj.File == 'PRE'){
                infoboxService.updatePre();
            } else if(jsonObj.File == 'MAIN'){
                infoboxService.updateTest(jsonObj.CycleAttr);
            } else if(jsonObj.File == 'POST'){
                infoboxService.updatePost();
            }
            if (jsonObj['FilesLoaded'] == true){
                infoboxService.updateRanges();
        }

            //infoboxService.addItem("true");
        }


        function onErrorItem(item, response, status, headers) {

            toastr.error(response.message, 'Error');
            $scope.uploadSuccess = false;

        }

    }

})()
