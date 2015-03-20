(function () {
  'use strict';

  angular
    .module('TestSite', [
      'TestSite.routes',
      'TestSite.authentication',
      'TestSite.project',
      'TestSite.import',
      'TestSite.layout',
      'TestSite.config',
      'ngAnimate'
    ]);

  angular
    .module('TestSite.routes', ['ui.router']);

  angular
    .module('TestSite.config', []);

})();
