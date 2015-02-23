(function () {
  'use strict';

  angular
    .module('TestSite.import', [
      'TestSite.import.controllers'
    ]);

  angular
    .module('TestSite.import.controllers', ['angularFileUpload','ngAnimate', 'toastr']);
})();