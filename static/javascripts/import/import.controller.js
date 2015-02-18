/**
* NavbarController
* @namespace TestSite.import.controllers
*/
(function () {
  'use strict';

  angular
  .module('TestSite.import.controllers' )
  .controller('ImportController', ImportController);

  ImportController.$inject = ['$scope', 'FileUploader'];

  /**
  * @namespace UploadController
  */
  function ImportController($scope, FileUploader) {
    $scope.uploader = new FileUploader();
    $scope.uploader.url = 'api/v1/data/import/'
    $scope.uploader.method = 'PUT'

    $scope.uploader.onBeforeUploadItem = onBeforeUploadItem;

    function onBeforeUploadItem(item) {
      item.formData.push({your: 'data'});
      console.log(item);
    }



  }




})();
