(function () {
  'use strict';

  angular
    .module('TestSite', [
      'TestSite.routes',
      'TestSite.authentication',
      'TestSite.layout',
      'TestSite.config'
    ]);

  angular
    .module('TestSite.routes', ['ngRoute']);

  angular
    .module('TestSite.config', []);

})();
