(function () {
  'use strict';

  angular
  .module('TestSite.routes')
  .config(config);

  config.$inject = ['$stateProvider', '$urlRouterProvider'];

  /**
  * @name config
  * @desc Define valid application routes -- DEPRECATED
  */
 //  function config($routeProvider) {
 //    $routeProvider.when('/register', {
 //      controller: 'RegisterController',
 //      controllerAs: 'vm',
 //      templateUrl: '/static/javascripts/authentication/register.html'
 //    }).when('/login', {
 //     controller: 'LoginController',
 //     controllerAs: 'vm',
 //     templateUrl: '/static/javascripts/authentication/login.html'
 //   }).when('/1065', {
 //     controller: 'StepController',
 //     controllerAs: 'vm',
 //     templateUrl: '/static/javascripts/layout/switch.html'
 //   }).otherwise('/');

 // }



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
    templateUrl: "/static/javascripts/layout/switch.html"
  })
  .state('1065.Import', {
    url: "/import",
    templateUrl: "/static/javascripts/import/upload.html",
    controller: "ImportController"
  }, { onEnter: function(){
   $('#reg').show();
 }
})
  .state('1065.Regression', {
    url: "/regression",
    templateUrl: "/static/javascripts/import/login.html"
  });
}





})();

