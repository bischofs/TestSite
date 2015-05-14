(function () {
  'use strict';

  angular
    .module('TestSite', [
	'TestSite.routes',
	'TestSite.infobox',
	'TestSite.delay',
	'TestSite.authentication',
	'TestSite.import',
	'TestSite.layout',
	'TestSite.config',
	'ngAnimate',
    ]);

  angular
    .module('TestSite.routes', ['ui.router']);

  angular
    .module('TestSite.config', []);

})();
