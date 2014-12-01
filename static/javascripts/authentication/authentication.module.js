(function () {
  'use strict';

  angular
    .module('TestSite.authentication', [
      'TestSite.authentication.controllers',
      'TestSite.authentication.services'
    ]);

  angular
    .module('TestSite.authentication.controllers', []);

  angular
    .module('TestSite.authentication.services', ['ngCookies']);
})();
