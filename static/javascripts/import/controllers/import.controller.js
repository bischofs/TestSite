/**
* NavbarController
* @namespace TestSite.import.controllers
*/
(function () {
  'use strict';

  angular
    .module('TestSite.import.controllers')
    .controller('UploadController', UploadController);

  UploadController.$inject = ['$scope', 'angularFileUpload'];

  /**
  * @namespace UploadController
  */
  function UploadController($scope, $upload) {
    var vm = this;
    $vm.$watch('files', function() {
      $vm.upload = $upload.upload({
        url: 'server/upload/url',
        data: {myObj: $vm.myModelObj},
        file: $vm.files
      }).progress(function(evt) {
        console.log('progress: ' + parseInt(100.0 * evt.loaded / evt.total) + '% file :'+ evt.config.file.name);
      }).success(function(data, status, headers, config) {
        console.log('file ' + config.file.name + 'is uploaded successfully. Response: ' + data);
      });

  });
  };

})();
