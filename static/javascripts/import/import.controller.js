/**
* NavbarController
* @namespace TestSite.import.controllers
*/
(function () {
  'use strict';

  angular
  .module('TestSite.import.controllers' )
  .controller('ImportController', ImportController);

  ImportController.$inject = ['$scope', 'FileUploader','toastr'];

  /**
  * @namespace UploadController
  */
  function ImportController($scope, FileUploader, toastr) {

    $scope.uploader = new FileUploader();
    $scope.uploader.url = 'api/v1/data/import/'
    $scope.uploader.method = 'POST'


    $scope.uploader.formData.push({cycle: 'FTP'});
    $scope.uploader.formData.push({bench: '1'});
    $scope.uploader.onSuccessItem = onSuccessItem;
    $scope.uploader.onErrorItem = onErrorItem;
    $scope.uploader.onBeforeUploadItem = onBeforeUploadItem;

    function  onBeforeUploadItem (item) {

      console.log();

    }


    function onSuccessItem(item, response, status, headers) {

     if (response.indexOf("Meta-Data missing") > -1){
       $scope.metaDataPresent = false;
     } else { $scope.metaDataPresent = true; }

     if(response.indexOf("units are not") > -1 || response.indexOf("Cannot find") > -1){
       $scope.requiredChannels = false;
     } else { $scope.requiredChannels = true; }

     if (response.indexOf("out of range") > -1){
       $scope.ambientConditions = false;
     } else { $scope.ambientConditions= true; }


   }

   function onErrorItem (item, response, status, headers) {
     toastr.error(response.message , 'Error');
     console.log()

   }




 }

})();
