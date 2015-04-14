(function () {
  'use strict';

  angular
    .module('TestSite.delay', [
      'TestSite.delay.controllers'
    ]);

  angular
    .module('TestSite.delay.controllers', ['angularCharts']);
})();
