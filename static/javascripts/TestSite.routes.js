(function () {
  'use strict';

  angular
    .module('TestSite.routes')
    .config(config);

  config.$inject = ['$routeProvider'];

  /**
  * @name config
  * @desc Define valid application routes
  */
  function config($routeProvider) {
    $routeProvider.when('/register', {
      controller: 'RegisterController',
      controllerAs: 'vm',
      templateUrl: '/static/javascripts/authentication/register.html'
    }).when('/login', {
	controller: 'LoginController',
	controllerAs: 'vm',
	templateUrl: '/static/javascripts/authentication/login.html'
    }).when('/1065', {
    	controller: 'UploadController',
    	controllerAs: 'vm',
    	templateUrl: '/static/javascripts/import/upload.html'
    }).otherwise('/');

  }

})();

