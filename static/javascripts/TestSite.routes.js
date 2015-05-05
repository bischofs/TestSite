(function () {
  'use strict';

  angular
  .module('TestSite.routes')
  .config(config);

  config.$inject = ['$stateProvider', '$urlRouterProvider'];

 function config($stateProvider, $urlRouterProvider){

  $urlRouterProvider.when('', '/index');

  $stateProvider.state('register', {
    url: "/register",
    templateUrl: "/static/javascripts/authentication/register.html",
    controller: 'RegisterController',
    controllerAs: 'vm'
  })
  .state('login', {
    url: "/login",
    templateUrl: "/static/javascripts/authentication/login.html",
    controller: 'LoginController',
    controllerAs: 'vm'
  })
  .state('1065', {
    url: "/1065",
    templateUrl: "/static/javascripts/layout/1065.html",
    controller: "InfoboxController"
  })
  .state('1065.Import', {
    url: "/import",
    templateUrl: "/static/javascripts/import/upload.html",
    controller: "ImportController"
  })
  .state('1065.Delay', {
    url: "/delay",
    templateUrl: "/static/javascripts/delay/delay.html",
    controller: "DelayController"
  });
}





})();

