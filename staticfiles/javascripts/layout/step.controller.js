/**
* StepController
* @namespace TestSite.layout
*/

(function() {
'use strict';

    angular
    .module('TestSite.layout.controllers')
    .controller('StepController',StepController);

    StepController.$inject = ['$scope'];

    function StepController($scope) {

        $scope.step = 1;
        $scope.setStep = function(step){
        $scope.step = step;
        }


    }


})();