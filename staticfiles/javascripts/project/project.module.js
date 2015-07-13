(function () {
  'use strict';

  angular
    .module('TestSite.project', [
      'TestSite.project.services',
      'TestSite.project.controllers'
    ]);

  angular
     .module('TestSite.project.controllers', []);

  angular
    .module('TestSite.project.services', ['ngCookies']);
})();
