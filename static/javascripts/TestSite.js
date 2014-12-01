(function () {
  'use strict';

  angular
    .module('TestSite', [
      'TestSite.routes',
      'TestSite.authentication',
	'Testsite.config'
    ]);

  angular
    .module('TestSite.routes', ['ngRoute']);

  angular
    .module('TestSite.config', []);

})();
