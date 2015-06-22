(function() {
    'use strict';

    angular
        .module('TestSite.results.controllers')
        .controller('ResultsController', ResultsController);

    ResultsController.$inject = ['$scope', '$http', 'toastr'];



    function ResultsController($scope, $http, toastr) {

        $scope.Calculation = function() {
            toastr.info('Calculations started!');
            $http.post('/api/v1/data/calculations/')
                .success(function(response) {
                    toastr.success(response.message, 'Calculations finished!');
                })
                .error(function(response) {
                    toastr.error(response.message, 'Calculations failed!');                    
                });

        };

        $scope.Report = function(){
            $http.get('/api/v1/data/calculations/')
                .success(function(response){
                    toastr.success(response.message, 'Report finished!');
		    location.href =('/api/v1/data/calculations/');
                })
                .error(function(response){
                    toastr.error(response.message, 'Report failed!');
                });
        }
    }

})();
