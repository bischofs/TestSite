/**
* NavbarController
* @namespace TestSite.import.controllers
*/
(function () {
  'use strict';

  angular
    .module('TestSite.import.controllers' )
    .controller('UploadController', UploadController);

 UploadController.$inject = ['$scope', 'FileUploader'];

  /**
  * @namespace UploadController
  */
  function UploadController($scope, FileUploader) {
    $scope.uploader = new FileUploader();
    $scope.uploader.url = 'api/v1/data/import/file'
    $scope.uploader.method = 'PUT'



  };

})();
