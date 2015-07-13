(function() {
    'use strict';

    angular
        .module('TestSite.routes')
        .config(config);

    config.$inject = ['$stateProvider', '$urlRouterProvider'];

    function config($stateProvider, $urlRouterProvider) {

        $urlRouterProvider.when('', '/index');

	$stateProvider.state('register', {
            url: "/register",
            templateUrl: "/1065/static/javascripts/authentication/register.html",
            controller: 'RegisterController',
            controllerAs: 'vm'
        })
            .state('login', {
                url: "/1065/login/",
                templateUrl: "/1065/static/javascripts/authentication/login.html",
                controller: 'LoginController',
                controllerAs: 'vm'
            })
            .state('Eval', {
                url: "/1065/evaluation/",
                templateUrl: "/1065/static/javascripts/layout/1065.html",
                controller: "InfoboxController"
            })
            .state('Eval.Import', {
                url: "import",
                templateUrl: "/1065/static/javascripts/import/upload.html",
                controller: "ImportController"
            })
            .state('Eval.Delay', {
                url: "delay",
                templateUrl: "/1065/static/javascripts/delay/delay.html",
                controller: "DelayController"
            })
            .state('Eval.Results', {
                url: "results",
                templateUrl: "/1065/static/javascripts/results/results.html",
                controller: "ResultsController"
            });
	
	
    }





})();
